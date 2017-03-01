"""Window to edit a scaling factor"""


__all__ = ["XScaleSpectrum"]


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
import a99
import f311.filetypes as ft
import f311.physics as ph


class XScaleSpectrum(a99.XLogDialog):

    def __init__(self, parent=None, file_main=None, file_abonds=None):
        a99.XLogDialog.__init__(self, parent)

        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        self.setWindowTitle("Scale spectrum")

        self.bandpasses = ph.get_ubv_bandpasses()

        # Internal flag to prevent taking action when some field is updated programatically
        self.flag_process_changes = False
        self.spectrum = None  # Spectrum object
        self.cmag = None
        self.factor_ = None

        # # Central layout
        lantanide = self.centralLayout = QVBoxLayout()
        a99.set_margin(lantanide, 0)
        self.setLayout(lantanide)

        # ## Horizontal splitter occupying main area: (options area) | (plot area)
        sp2 = self.splitter2 = QSplitter(Qt.Horizontal)
        lantanide.addWidget(sp2)

        ###
        wleft = keep_ref(QWidget())
        lwleft = QVBoxLayout(wleft)
        a99.set_margin(lwleft, 3)
        ###
        # lwleft.addWidget(keep_ref(QLabel("<b>Reference band</b>")))
        # ###

        lgrid = keep_ref(QGridLayout())
        lwleft.addLayout(lgrid)
        a99.set_margin(lgrid, 0)
        lgrid.setVerticalSpacing(4)
        lgrid.setHorizontalSpacing(5)

        # field map: [(label widget, edit widget, field name, short description, long description), ...]
        map = self._map0 = []
        signals = []  # for the SignalProxy below
        ###
        x = keep_ref(QLabel())
        y = self.cb_band = QComboBox()
        signals.append(y.currentIndexChanged)
        x.setBuddy(y)
        y.addItems([bp.name for bp in self.bandpasses])
        map.append((x, y, "&Band name", "UBVRI-x system", ""))
        ###
        x = keep_ref(QLabel())
        y = self.cb_system = QComboBox()
        signals.append(y.currentIndexChanged)
        x.setBuddy(y)
        y.addItems(["ab", "vega", "stdflux"])
        map.append((x, y, "Magnitude &system",
                   "<b>'ab'</b>: AB[solute]<br>"
                   "<b>'vega'</b>: uses Vega spectrum as reference;<br>"
                   "<b>'stdflux'</b>: uses standard reference values<br>from literature", ""))
        ###
        x = self.label_zero_point = QLabel()
        y = self.spinBox_zero_point = QDoubleSpinBox()
        y.setSingleStep(.01)
        y.setDecimals(3)
        y.setMinimum(-100)
        y.setMaximum(100)
        signals.append(y.valueChanged)
        x.setBuddy(y)
        map.append((x, y, "&Zero point", "Value to subtract from calculated magnitude", ""))
        ###
        x = self.label_x = QLabel()
        y = self.checkbox_force_band_range = QCheckBox()
        signals.append(y.stateChanged)
        x.setBuddy(y)
        map.append((x, y, "&Force filter range?", "(even when spectrum does not<br>completely overlap filter)", ""))
        ###
        x = self.label_x = QLabel()
        y = self.spinBox_mag = QDoubleSpinBox()
        y.setSingleStep(.1)
        y.setDecimals(3)
        y.setMinimum(-100)
        y.setMaximum(100)
        signals.append(y.valueChanged)
        x.setBuddy(y)
        map.append((x, y, "Desired apparent &magnitude", "", ""))
        ###

        for i, (label, edit, name, short_descr, long_descr) in enumerate(map):
            # label.setStyleSheet("QLabel {text-align: right}")
            assert isinstance(label, QLabel)
            label.setText(a99.enc_name_descr(name, short_descr))
            label.setAlignment(Qt.AlignRight)
            lgrid.addWidget(label, i, 0)
            lgrid.addWidget(edit, i, 1)
            label.setToolTip(long_descr)
            edit.setToolTip(long_descr)

        # ### Text Edit To Show calculated results
        x = self.keep_ref(QLabel("<b>Computations</b>"))
        y = self.textEdit = QTextEdit()
        x.setBuddy(y)
        y.setReadOnly(True)
        y.setStyleSheet("QTextEdit {color: %s}" % a99.COLOR_DESCR)
        lwleft.addWidget(x)
        lwleft.addWidget(y)

        bb = keep_ref(QDialogButtonBox())
        bb.setOrientation(Qt.Horizontal)
        bb.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        lwleft.addWidget(bb)

        bb.rejected.connect(self.reject)
        bb.accepted.connect(self.accept)

        # #### Plot area
        wright = keep_ref(QWidget())
        self.figure0, self.canvas0, self.lfig0 = a99.get_matplotlib_layout(wright)

        sp2.addWidget(wleft)
        sp2.addWidget(wright)

        # # Signal proxy
        # Limits the number of times that on_sth_changed() is called
        self.signal_proxy = a99.SignalProxy(signals, delay=0.3, rateLimit=0, slot=self.on_sth_changed)

        self.setEnabled(False)  # disabled until load() is called
        a99.style_checkboxes(self)
        self.flag_process_changes = True

        # self.__update()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Getters & setters


    def band_index(self):
        return self.cb_band.currentIndex()

    def band_name(self):
        return str(self.cb_band.currentText())

    def set_spectrum(self, x):
        assert isinstance(x, ft.Spectrum)
        self.spectrum = x
        self.setEnabled(True)
        self.__update()

    def set_band_name(self, x):
        self.cb_band.setEditText(x)
        self.__update()

    def system(self):
        return str(self.cb_system.currentText())

    def set_system(self, x):
        self.cb_system.setEditText(x)
        self.__update()

    def flag_force_band_range(self):
        return self.checkbox_force_band_range.isChecked()

    def set_flag_force_band_range(self, x):
        self.checkbox_force_band_range.setChecked(bool(x))
        self.__update()

    def desired_magnitude(self):
        return self.spinBox_mag.value()

    def zero_point(self):
        return self.spinBox_zero_point.value()

    def calculated_magnitude(self):
        return self.cmag

    def factor(self):
        return self.factor_

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Qt override

    def accept(self):
        if self.factor_ is None or np.isinf(self.factor_):
            _ = QMessageBox.critical(None, "Cannot scale", "Scaling factor cannot be calculated")
            return False
        QDialog.accept(self)

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Slots

    def on_sth_changed(self):
        if self.flag_process_changes:
            self.__update()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Internal gear
            

    def __update(self):
        self.flag_process_changes = False
        try:
            fig = self.figure0
            fig.clear()
            # name = self.band_name()
            bandpass = self.bandpasses[self.band_index()]
            mag_data = ph.calculate_magnitude(self.spectrum, bandpass, self.system(), self.zero_point(),
                                              self.flag_force_band_range())
            _draw_figure(fig, mag_data, self.spectrum, self.flag_force_band_range())
            self.canvas0.draw()

            mag = self.desired_magnitude()
            cmag = mag_data["cmag"]

            self.factor_ = k = ph.MAGNITUDE_BASE ** (cmag - mag) if cmag is not None else float("nan")

            # Updates calculated state

            kk = mag_data.keys()
            lenk = max([len(k) for k in kk])
            vv = mag_data.values()
            text = "\n".join(["{0:{1}}: {2}".format(k, lenk, v) for k, v in mag_data.items()])


            self.textEdit.setText("<pre>\n%s\n\n"
                                  "Scaling factor: %g"
                                  "</pre>" % (text, self.factor_))

        except Exception as E:
            self.add_log_error(str(E))
            a99.get_python_logger().exception("Could not plot band_curve")
        finally:
            self.flag_process_changes = True



def _draw_figure(fig, mag_data, spectrum, flag_force_band_range):
    from f311 import explorer as ex

    # y = s*f ; s and y: fluxes ; f: filter ; all functions of wavelength
    # out_area = integrate y over whole axis, but y = 0 outside the filter range
    # weighted_mean_flux = out_area/band_area


    bp = mag_data["bp"]
    weighted_mean_flux = mag_data["weighted_mean_flux"]
    calc_l0, calc_lf = mag_data["calc_l0"], mag_data["calc_lf"]
    filtered_sp = mag_data["filtered_sp"]
    band_area = bp.area(calc_l0, calc_lf)
    out_y = filtered_sp.y
    out_area = np.trapz(filtered_sp.y, filtered_sp.x)
    cmag = mag_data["cmag"]

    MARGIN_H = .15  # extends horizontally beyond band range
    MARGIN_V = .2  # extends vertically beyond band range
    COLOR_OTHER_BANDS = (.4, .4, .4)
    COLOR_CURRENT_BAND = (.1, .1, .1)
    COLOR_FILL_BAND = (.9, .8, .8)
    LINE_WIDTH = 1.5
    band_x = np.linspace(bp.l0, bp.lf, 200)
    band_y = bp.ufunc()(band_x)
    band_span_x = bp.lf - bp.l0
    band_max_y = max(band_y)
    plot_l0, plot_lf = bp.l0 - band_span_x * MARGIN_H, bp.lf + band_span_x * MARGIN_H
    plot_h_middle = (plot_l0 + plot_lf) / 2
    spp = ex.SB_Cut(plot_l0, plot_lf).use(spectrum)  # spectrum for plotting
    flux_ylim = [0, np.max(spp.y) * (1 + MARGIN_V)] if len(spp) > 0 else [-.1, .1]

    # # First subplot
    ax = ax0 = fig.add_subplot(311)
    if len(spp) == 0:
        ax.plot([], [])
        ax.annotate("Band out of spectral range [%g, %g]" % (spectrum.x[0], spectrum.x[-1]), xy=(plot_h_middle, 0),
                    horizontalalignment="center", verticalalignment="center")
    else:
        ax.plot(spp.x, spp.y, c=COLOR_CURRENT_BAND, lw=LINE_WIDTH)
        # shows weighted mean flux within range (flat spectrum that would have the same
        # magnitude as the actual spectrum)
        ax.plot([calc_l0, calc_lf], [weighted_mean_flux, weighted_mean_flux], linestyle="dashed",
                linewidth=LINE_WIDTH, color=(.4, .3, .1))
    # ax.plot(spc.x, spc.y, c=COLOR_CURRENT_BAND, lw=LINE_WIDTH, zorder=999)
    ax.set_ylim(flux_ylim)
    ax.set_ylabel("Flux")

    # # Second subplot
    overall_max_y = 0
    ax = fig.add_subplot(312, sharex=ax0)
    # other bands
    for band in ph.get_ubv_bandpasses():
        if band.lf >= plot_l0 and band.l0 <= plot_lf:
            x = np.linspace(band.l0, band.lf, 200)
            y = band.ufunc()(x)
            ax.plot(x, y, lw=LINE_WIDTH)  # c=COLOR_OTHER_BANDS)
            idx_max = np.argmax(y)
            max_y = y[idx_max]
            overall_max_y = max(max_y, band_max_y)
            ax.annotate(band.name, xy=(x[idx_max], y[idx_max] + .1),
                        horizontalalignment="center", verticalalignment="center")
    # current band
    ax.plot(band_x, band_y, c=COLOR_CURRENT_BAND, lw=LINE_WIDTH)
    xfill = np.linspace(calc_l0, calc_lf, 50)
    yfill = bp.ufunc()(xfill)
    ax.fill_between(xfill, yfill, color=COLOR_FILL_BAND)
    ax.set_ylim([0, overall_max_y * (1 + MARGIN_V)])
    ax.set_ylabel("Bandpass filter curve")
    idx_max = np.argmax(band_y)
    ax.annotate("A1=%.1f" % band_area, xy=(band_x[idx_max], band_max_y * .45),
                horizontalalignment="center", verticalalignment="center",
                color=(.4, .2, .1))

    # Third subplot
    # # First subplot
    ax = fig.add_subplot(313, sharex=ax0)
    if len(filtered_sp) == 0:
        ax.plot([], [])
        ax.annotate("Band out of spectral range [%g, %g]" % (spectrum.x[0], spectrum.x[-1]), xy=(plot_h_middle, 0),
                    horizontalalignment="center", verticalalignment="center")
    else:
        ax.plot(filtered_sp.x, out_y, c=COLOR_CURRENT_BAND, lw=LINE_WIDTH)
        ax.fill_between(filtered_sp.x, out_y, color=COLOR_FILL_BAND)
        
        ax.plot(xfill, yfill*weighted_mean_flux, linestyle="dashed",
                linewidth=LINE_WIDTH, color=(.4, .3, .1), label='equivalent flat')
        ax.annotate("A2=%g" % out_area, xy=((xfill[0] + xfill[-1]) / 2, max(out_y) * .45),
                    horizontalalignment="center", verticalalignment="center",
                    color=(.4, .2, .1))
    ax.set_xlim([plot_l0, plot_lf])
    ax.set_ylabel("Filtered flux")
    ax.set_ylim(flux_ylim)
    ax.set_xlabel("Wavelenght ($\AA$)")

    fig.tight_layout()

    return weighted_mean_flux, cmag



def _toggle_widget(w, flag_readonly):
    w.setReadOnly(flag_readonly)
    sheet = ""
    if flag_readonly:
        sheet = "QWidget {background: #A09D9D}"
    w.setStyleSheet(sheet)

