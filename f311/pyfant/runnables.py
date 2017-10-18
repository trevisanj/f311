import subprocess
from .conf import *
import os
from .errors import *
from threading import Lock
import a99
from .. import filetypes as ft
from collections import OrderedDict

__all__ = ["Runnable", "RunnableStatus", "ExecutableStatus", "Executable",
           "Innewmarcs", "Hydro2", "Pfant", "Nulbad", "Combo"]


@a99.froze_it
class RunnableStatus(object):

    def __init__(self, runnable):
        assert isinstance(runnable, Runnable)
        self.runnable = runnable

    def __str__(self):
        l = []
        if self.runnable.flag_finished:
            l.append("finished")
        if self.runnable.flag_running:
            l.append("running")
        if self.runnable.flag_killed:
            l.append("*killed*")
        if self.runnable.flag_error:
            l.append("*error*")
        if self.runnable.error_message:
            l.append("*" + str(self.runnable.error_message) + "*")
        if len(l) > 0:
            return " ".join(l)
        return "?"

@a99.froze_it
class ExecutableStatus(object):
    """Stores status related to Executable for reporting purposes."""
    
    def __init__(self, executable):
        assert isinstance(executable, Executable)
        self.exe_filename = executable.__class__.__name__.lower()
        self.executable = executable
        # used by pfant only
        self.ikey = None
        # used by pfant only
        self.ikeytot = None

    def __str__(self):
        l = []
        if self.exe_filename is not None:
            l.append(self.exe_filename)
        if self.executable.flag_finished:
            l.append("finished")
        if self.executable.flag_running:
            l.append("running")
        if self.executable.flag_killed:
            l.append("*killed*")
        if self.executable.flag_error:
            l.append("*error*")
        if self.executable.error_message:
            l.append("*" + str(self.executable.error_message) + "*")
        if self.ikey is not None:
            l.append("%5.1f %% (%d/%d)" % (100.*self.ikey/self.ikeytot, self.ikey, self.ikeytot))
        if self.executable.returncode is not None:
            l.append("returncode=%d" % self.executable.returncode)
        if len(l) > 0:
            return " ".join(l)
        return "?"


class Runnable(object):
    """
    Object with a run() method.

    The run() method is blocking, i.e., it only returns when running is done.

    This is a base class for Executable and Combo.
    """

    @property
    def flag_finished(self):
        return self._flag_finished
    @property
    def flag_running(self):
        return self._flag_running
    @property
    def flag_killed(self):
        return self._flag_killed
    @property
    def flag_error(self):
        return self._flag_error
    @property
    def error_message(self):
        return self._error_message
    @property
    def flag_success(self):
        return self._flag_finished and not self._flag_error and not self._flag_killed

    @property
    def sid(self):
        return self._get_sid()

    @property
    def result(self):
        return self._result

    def __init__(self):
        self.name = a99.random_name()
        # Is running?
        self._flag_running = False
        # Is finished?
        self._flag_finished = False
        # Was killed?
        self._flag_killed = False
        # Had error?
        self._flag_error = False
        # Will contain error message if finished with error
        self._error_message = ""
        # Will contain results DataFile objects (keys vary depending on the Runnable subclass
        self._result = {}

    def get_status(self):
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()

    def kill(self):
        raise NotImplementedError()

    def load_result(self):
        """Abstract. Override this method to open the result file(s) particular to the
        executable.

        Methods in subclasses should populate self._result
        """

    def reset(self):
        """Prepares to run again."""
        assert not self._flag_running, "Cannot reset if running"
        self._flag_finished = False
        self._flag_killed = False
        self._flag_error = False
        self._error_message = ""
        if self.sid.id:
            self.sid.clean(False)

    def clean(self, *args):
        """Wraps self.sid.clean(). See ftpyfant.SID"""
        self.sid.clean(*args)

    def _get_sid(self):
        raise NotImplementedError()


class Executable(Runnable):
    """
    PFANT executables common ancestor class.
    """

    # Set at descendant class with a ftpyfant.conf.FOR_* value
    sequence_index = -1

    @property
    def returncode(self):
        return self.__returncode

    @property
    def exe_path(self):
        return self._exe_path

    @exe_path.setter
    def exe_path(self, x):
        self._exe_path = x

    @property
    def conf(self):
        return self.__conf

    @conf.setter
    def conf(self, x):
        self.__conf = x

    @property
    def opt(self):
        """Wraps self.__conf.opt"""
        return self.__conf.opt

    @opt.setter
    def opt(self, x):
        """Wraps self.__conf.opt"""
        self.__conf.opt = x

    def __init__(self):
        Runnable.__init__(self)
        # # Protected variables
        # Full path to executable (including executable name)
        self._exe_path = "none"
        # ExecutableStatus instance
        self._status = ExecutableStatus(self)

        # # Private variables
        # fill be filled with self.popen.returncode in due time
        self.__returncode = None
        # Created by _run()
        self.__popen = None
        # Conf instance
        self.__conf = Conf()

    def run(self):
        """Runs executable.

        Blocking routine. Only returns when executable finishes running.
        """
        assert not self._flag_running, "Already running"
        assert not self._flag_finished, "Already finished"
        self.conf.configure([self.sequence_index])
        try:
            self.conf.logger.debug("Running %s '%s'" % (self.__class__.__name__.lower(), self.name))
            self.__run()
        finally:
            self.conf.close_popen_text_dest()

    def run_from_combo(self):
        """Alternative to run executable (called from Combo class).

        This routine bypasses all the configuration that is done prior to running.
        (Combo.configure() will do the necessary configuration).
        """
        assert not self._flag_running, "Already running"
        assert not self._flag_finished, "Already finished"
        self.__run()

    def kill(self):
        self._flag_killed = True
        if self._flag_running:
            self.__popen.kill()

    def get_status(self):
        return self._status

    def _get_sid(self):
        return self.__conf.sid

    def __run(self):
        """Called both from run() and run_from_combo()."""
        args = self.conf.get_args()
        cmd_words = [self._exe_path] + args

        s = " ".join(cmd_words)
        self.conf.logger.debug(s)
        # logs command-line to file and closes it.
        with open(self.conf.sid.join_with_session_dir("commands.log"), "a") as h:
            h.write(s+"\n\n")
        emsg = ""
        try:
            self.__popen = subprocess.Popen(cmd_words, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            # if self.__stdout:
            #     self.__popen = subprocess.Popen(cmd_words, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # else:
            #     self.__popen = subprocess.Popen(cmd_words)
            self._flag_running = True
            try:
                if self.conf.popen_text_dest is not None:
                    for line in self.__popen.stdout:
                        # In Python 3, line is bytes, write() cannot deal with that
                        self.conf.popen_text_dest.write(line.decode("ascii"))
            finally:
                self.__popen.stdout.close()


#todo cleanup
#                 self._flag_running = True
#
#                 if self.__stdout:  # TODO disabled PIPE stdout for popen
#                     try:
#                         for line in self.__popen.stdout:
#                             self.__stdout.write(line)
#                     finally:
#                         # todo cleanup
#                         # printOpenFiles()
#
#                         self.__popen.stdout.close()
#                         self.__stdout.close()
#
# #todo cleanup
#                         # print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
#                         # printOpenFiles()
#                         # sys.exit()

            # blocks execution until finished
            self.__popen.wait()
            self.__popen.poll()

            if self.__popen.returncode != 0:
                raise FailedError("%s failed (returncode=%s)" % (self.__class__.__name__.lower(), self.__popen.returncode))

        except Exception as e:
            flag_re_raise = True
            if self.__popen:
                self.__popen.poll()
                if isinstance(e, FailedError) and self._flag_killed:
                    # dismisses error if explicitly killed
                    flag_re_raise = False
                elif isinstance(e, IOError) and self.__popen.returncode == 0:
                    # Sometimes a IOError is raised even if Fortran executes
                    # successfully, so the error is dismissed
                    self.conf.logger.warning("Harmless error in: %s %s" %
                     (self.conf.sid.dir, self.get_status()))
                    self.conf.logger.warning(str(e))
                    flag_re_raise = False

            if flag_re_raise:
                self._error_message = e.__class__.__name__+": "+str(e)
                self._flag_error = True
                raise
        finally:
            self._flag_finished = True
            self._flag_running = False
            if self.__popen is not None:
                self.__returncode = self.__popen.returncode
            self.conf.logger.debug(str(self._status))


@a99.froze_it
class Innewmarcs(Executable):
    """Class representing the innewmarcs executable."""

    sequence_index = FOR_INNEWMARCS

    def __init__(self):
        Executable.__init__(self)
        self._exe_path = "innewmarcs"

        # FileModBin object
        self.modeles = None

    def load_result(self):
        file_mod = ft.FileModBin()
        filepath = self.conf.get_fn_modeles()
        file_mod.load(filepath)
        # Assigns .modeles for backward compatibility
        self.modeles = self._result["modeles"] = file_mod


@a99.froze_it
class Hydro2(Executable):
    """Class representing the hydro2 executable."""

    sequence_index = FOR_HYDRO2

    def __init__(self):
        Executable.__init__(self)
        self._exe_path = "hydro2"

    def load_result(self):
        """
        Makes self._result["profiles"] = {filename0: FileToH0, filename1: FileToH1, ...}

        Tolerant to non-existing files, but will crash if existing files pointed to at the
        FileHmap fail to load.
        """

        fhmap = self.conf.get_file_hmap()
        if fhmap is None:
            raise RuntimeError("Cannot find my hmap file")

        profiles = self._result["profiles"] = OrderedDict()
        for row in fhmap.rows:
            value = None
            if os.path.exists(row.fn):
                fh = ft.FileToH()
                fh.load(row.fn)
                value = fh

            profiles[row.fn] = value



@a99.froze_it
class Pfant(Executable):
    """Class representing the pfant executable."""

    sequence_index = FOR_PFANT

    def __init__(self):
        Executable.__init__(self)
        self._exe_path = "pfant"  # Path to PFANT executable (including executable name)

        # ** Variables assigned by poll_progress()
        self.ikey = None  # Current iteration (Fortran: ikey)
        self.ikeytot = None  # Current iteration (Fortran: ikeytot)

        # # Spectra loaded after pfant runs if self.flag_open_result is True

        # .spec file, e.g., flux.spec
        self.spec = None
        # .cont file, e.g., flux.cont
        self.cont = None
        # .norm file, e.g., flux.norm
        self.norm = None

    def get_status(self):
        """
        Tries to open progress indicator file. If succeeds, stores
        current iteration in attribute ikey, and
        number of iterations in attribute ikeytot.

        """
        p = self.conf.opt.fn_progress or "progress.txt"
        ret = self._status
        if (not self.ikey or self.ikey < self.ikeytot) and os.path.isfile(p):
            with open(p) as h:
                try:
                    t = list(map(int, h.readline().split("/")))
                    ret.ikey = t[0]
                    ret.ikeytot = t[1]
                except ValueError:
                    # Ignores conversion errors
                    pass
        return ret

    def load_result(self):

        for type_ in ("norm", "cont", "spec"):
            filepath = self.conf.get_pfant_output_filepath(type_)
            file_sp = ft.FileSpectrumPfant()
            file_sp.load(filepath)
            self.__setattr__(type_, file_sp.spectrum)
            self._result[type_] = file_sp.spectrum


@a99.froze_it
class Nulbad(Executable):
    """Class representing the nulbad executable."""

    sequence_index = FOR_NULBAD

    def __init__(self):
        Executable.__init__(self)
        self._exe_path = "nulbad"

        # nulbad output
        self.convolved = None

    def load_result(self):
        file_sp = ft.FileSpectrumNulbad()
        filepath = self.conf.get_nulbad_output_filepath()
        file_sp.load(filepath)
        self.convolved = file_sp.spectrum
        self._result["convolved"] = file_sp.spectrum


@a99.froze_it

class Combo(Runnable):
    """
    Runs sequence of executables: innermarcs, hydro2, pfant, nulbad.

    Args:
      sequence (optional): sequence of executables to run. Defaults to
        [e_innewmarcs, e_hydro2, e_pfant, e_nulbad]. If you want to run only
        pfant and nulbad, for example, you can pass [e_pfant, e_nulbad]

    There are several restrictions imposed
    - files are created inside a session directory such as session123456
    - all four executables must be in the same directory
    """

    @property
    def running_exe(self):
        """Returns the current or last running exe."""
        return self.__running_exe

    @property
    def exe_dir(self):
        return self.__exe_dir
    @exe_dir.setter
    def exe_dir(self, x):
        self.__exe_dir = x

    @property
    def sequence(self):
        return self.__sequence
    @sequence.setter
    def sequence(self, x):
          self.__sequence = x

    @property
    def innewmarcs(self):
        return self.__innewmarcs

    @property
    def hydro2(self):
        return self.__hydro2

    @property
    def pfant(self):
        return self.__pfant

    @property
    def nulbad(self):
        return self.__nulbad

    @property
    def conf(self):
        return self.__conf

    @conf.setter
    def conf(self, x):
        self.__conf = x

    def __init__(self, sequence=None):
        Runnable.__init__(self)
        # # Configuration
        # Directory containing the 4 executables
        self.__exe_dir = ""
        # Whether to display Fortran messages in the terminal.
        # Note: a file named "<session dir>/fortran.log" is always created.
        self.__flag_log_console = True

        # Executables to run
        # order is irrelevant (will be sorted anyway).
        self.__sequence = [FOR_INNEWMARCS, FOR_HYDRO2, FOR_PFANT, FOR_NULBAD] \
            if sequence is None else translate_sequence(sequence)

        # ** Executable instances
        self.__innewmarcs = Innewmarcs()
        self.__hydro2 = Hydro2()
        self.__pfant = Pfant()
        self.__nulbad = Nulbad()

        # ** Internal variables
        self.__running_exe = None  # Executable object currently running
        # ComboStatus instance
        self.__status = RunnableStatus(self)
        # Conf instance
        self.__conf = Conf()

    def get_exes(self):
        """Returns exe objects in a list according with self.sequence."""

        map = [(FOR_INNEWMARCS, self.__innewmarcs), (FOR_HYDRO2, self.__hydro2), (FOR_PFANT, self.__pfant),
               (FOR_NULBAD, self.__nulbad)]
        res = []
        ii, ee = list(zip(*map))
        self.__sequence.sort()
        for i_exe in self.__sequence:
            if i_exe in ii:
                res.append(ee[ii.index(i_exe)])
        return res

    def run(self):
        assert not self._flag_running, "Already running"
        assert not self._flag_finished, "Already finished"
        self._flag_running = True
        try:
            self.conf.configure(self.__sequence)
            self.conf.logger.debug("Running %s '%s'" % (self.__class__.__name__.lower(), self.name))
            for e in self.get_exes():
                self.__running_exe = e
                e.conf = self.conf
                e.run_from_combo()
        except Exception as e:
            self._flag_error = True
            self._error_message = "Combo: "+str(e)
            raise
        finally:
            self.conf.close_popen_text_dest()
            self._flag_running = False
            self._flag_finished = True

    def load_result(self):
        """Calls load_result() for all contained executables, then collects all into self._result"""
        for exe in self.get_exes():
            exe.load_result()

            # Bug checking: Executables must not repeat the names of their results,
            # so that they can be all collected in Combo._result
            for key in exe._result:
                if key in self._result:
                    raise AssertionError("Key '{}' is in {} but was seen previously by Combo".
                                         format(key, exe.__class__))
            self._result.update(exe._result)

    def kill(self):
        self._flag_killed = True
        if self._flag_running:
            if self.__running_exe:
                self.__running_exe.kill()

    def get_status(self):
        """Returns status of running executable or self._status."""
        if self.__running_exe:
            return self.__running_exe.get_status()
        else:
            return self.__status

    def reset(self):
        Runnable.reset(self)
        ee = self.get_exes()
        for e in ee:
            e.reset()

    def _get_sid(self):
        return self.__conf.sid
