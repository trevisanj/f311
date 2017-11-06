"""
Class to store all command-line options & DataFile instances used to run one or more
executables.
"""

__all__ = ["Conf", "FOR_INNEWMARCS", "FOR_HYDRO2", "FOR_PFANT",
           "FOR_NULBAD", "IdMaker", "SID", "translate_sequence"]


import shutil
import os
import logging
import subprocess
from threading import Lock
import a99
from .. import filetypes as ft


# Indexes to use in Conf.sequence property
FOR_INNEWMARCS = 0
FOR_HYDRO2 = 1
FOR_PFANT = 2
FOR_NULBAD = 3

_sequence_dict = {"innewmarcs": FOR_INNEWMARCS, "hydro2": FOR_HYDRO2, "pfant": FOR_PFANT, "nulbad": FOR_NULBAD}

def translate_sequence(sequence):
    """Convenience/tolerance function to convert strings with executable names to FOR_*"""
    ret = []
    return [_sequence_dict[x] if isinstance(x, str) else x for x in sequence]

@a99.froze_it
class SID(object):
    """
    SID -- Session Id and Directory

    Part of code that finds new session id and creates corresponding directory
    """

    @property
    def id(self):
        """
        Information used to create a session directory and to identify this directory.

        When this property is set, the session directory
        (probably named "session-<session_id>") is created
        immediately."""
        return self.__id

    @id.setter
    def id(self, x):
        assert self.__id is None, "Session id already set to \"%s\"" % self.__id
        new_dir = self.__id_maker.session_prefix_singular+x
        os.mkdir(new_dir)
        self.__id = str(x)
        self.__dir = new_dir
        # Will raise if directory exists: directory names must be unique.

    @property
    def dir(self):
        """Name made up with a prefix + (the session id)."""
        return self.__dir

    @property
    def flag_split_dirs(self):
        """Split sessions into several directories with 1000 sessions maximum each.

        This option was created to speed up directory access."""
        return self.__flag_split_dirs
    @flag_split_dirs.setter
    def flag_split_dirs(self, x):
        self.__flag_split_dirs = x

    @property
    def id_maker(self):
        """IdMaker instance"""
        return self.__id_maker
    @id_maker.setter
    def id_maker(self, x):
        self.__id_maker = x

    def __init__(self, id_maker):
        assert isinstance(id_maker, IdMaker)
        self.__id_maker = id_maker
        self.__id = None
        self.__dir = None
        self.__flag_split_dirs = False

    def join_with_session_dir(self, fn):
        """Joins self.session_dir with specified filename to make a path."""
        return os.path.join(self.__dir, fn)

    def make_id(self):
        """Finds an id for a new session and creates corresponding
        directory.

        Directory must be created, otherwise two concurrent threads may grab
        the same id.
        """

        # assert self.session_id is None, "Session id already made"

        if self.__id is not None:
            return
        self.__id, self.__dir = \
            self.__id_maker.make_id(self.__flag_split_dirs)

    def clean(self, flag_remove_dir=True):
        """Deletes session directory with all files inside.

        Args:
          flag_remove_dir=True: if not set, will only delete the contents,
            keeping the directory
        """

        if flag_remove_dir:
            logging.debug("About to remove directory '%s'" % self.__dir)
            shutil.rmtree(self.__dir)
        else:
            # reference: http://stackoverflow.com/questions/185936/delete-folder-contents-in-python
            for the_file in os.listdir(self.__dir):
                file_path = os.path.join(self.__dir, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except:
                    self.logger.exception("Error removing '%s'" % the_file)


# # Section id managhement
# Part of code that finds new session id and creates corresponding directory


class IdMaker(object):
    """
    Thread-safe id maker + directory maker functionality.
    """

    def __init__(self):
        from f311 import pyfant as pf
        self.dirs_per_dir = 1000  # only if flag_split_dirs
        self.session_prefix_singular = pf.SESSION_PREFIX_SINGULAR
        self.session_prefix_plural = pf.SESSION_PREFIX_PLURAL
        # Lock is necessary to make unique session ids
        self.__lock_session_id = Lock()
        self.__i_id = 0

    def make_id(self, flag_split_dirs):
        """Makes session id and creates corresponding directory.

        This routine is thread-safe.
        """
        with self.__lock_session_id:
            while True:
                new_dir = self.get_session_dirname(flag_split_dirs)
                self.__i_id += 1
                if not os.path.isdir(new_dir):
                    new_id = "%d" % self.__i_id
                    break
            os.makedirs(new_dir)
            return new_id, new_dir

    def get_session_dirname(self, flag_split_dirs):
        """Returns string which is the name of a filesystem directory."""
        if not flag_split_dirs:
            return self.session_prefix_singular+str(self.__i_id)
        d0 = self.session_prefix_plural+\
             str(int(self.__i_id//self.dirs_per_dir)*self.dirs_per_dir)
        d1 = self.session_prefix_singular+str(self.__i_id)
        return os.path.join(d0, d1)

@a99.froze_it
class Conf(object):
    """
    Class holds the configuration of an executable.

    Most options are initialized do None. This means that they won't be added to the
    command line.
    """

    @property
    def popen_text_dest(self):
        """(Read-only) File-like object to act as destination to popen text messages."""
        return self.__popen_text_dest

    @property
    def flag_log_console(self):
        """Display Fortran messages in console (default=True)?"""
        return self.__flag_log_console

    @flag_log_console.setter
    def flag_log_console(self, x):
        self.__flag_log_console = x

    @property
    def flag_log_file(self):
        """Log Fortran messages to "<session dir>/fortran.log" (default=True)?"""
        return self.__flag_log_file

    @flag_log_file.setter
    def flag_log_file(self, x):
        self.__flag_log_file = x

    @property
    def flag_output_to_dir(self):
        """Tweak output filenames to be created inside the session directory
        (default=False)?"""
        return self.__flag_output_to_dir
    @flag_output_to_dir.setter
    def flag_output_to_dir(self, x):
        self.__flag_output_to_dir = x

    @property
    def logger(self):
        if not self.__logger:
            self.__logger = a99.get_python_logger()
        return self.__logger

    @logger.setter
    def logger(self, x):
        self.__logger = x

    @property
    def sid(self):
        """SID object"""
        return self.__sid

    @sid.setter
    def sid(self, x):
        self.__sid = x

    @property
    def opt(self):
        """FileOptions object"""
        return self.__opt

    @opt.setter
    def opt(self, x):
        self.__opt = x


    def __init__(self):
        # # Setup flags
        self.__flag_log_console = True
        self.__flag_log_file = True
        self.__flag_output_to_dir = False

        # # DataFile instances
        # See create_data_files() to see what happens when one or more
        # of these objects is set.
        # running the executable.
        # ## FileMain instance
        self.file_main = None
        # ## FileAbonds instance
        self.file_abonds = None
        # ## FileAbonds instance
        self.file_dissoc = None
        # ## FileHmap instance
        self.file_hmap = None
        # ## FileAtoms instance
        self.file_atoms = None
        # ## FileMolecules instance
        self.file_molecules = None

        # # Command-line options
        self.__opt = ft.FileOptions()

        # # Read-only properties
        self.__popen_text_dest = None
        self.__logger = None
        self.__sid = SID(_conf_id_maker())


        # # Internals
        self.__flag_configured_before = False

    def configure(self, sequence):
        """Series of configuration actions to take before Runnable can run.

        Runnable can be re-run (useful if fails), so configure() will know
        if it has been called before and skip most operations if so.
        """
        if not self.__flag_configured_before:
            self.__logger = a99.get_python_logger()
            self.__sid.make_id()
            if self.__flag_output_to_dir:
                self.__rename_outputs(sequence)
            if FOR_PFANT in sequence:
                self.__opt.fn_progress = self.__sid.join_with_session_dir("progress.txt")  # this is for pfant

        # Always gotta open logs
        if self.__flag_log_file:
            log_path = self.__sid.join_with_session_dir("fortran.log")
            if self.__flag_log_console:
                stdout_ = a99.LogTwo(log_path)
            else:
                stdout_ = open(log_path, "w")
        else:
            if self.__flag_log_console:
                stdout_ = subprocess.STD_OUTPUT_HANDLE
            else:
                stdout_ = None
        self.__popen_text_dest = stdout_


        self.__create_data_files()
        self.__flag_configured_before = True

    def close_popen_text_dest(self):
        """Closes self.popen_text_dest opened in configure().

        To be called after the Runnable runs."""
        if self.__popen_text_dest is not None:
            self.__popen_text_dest.close()

    def get_file_main(self, opt=None):
        """Tries to figure out a FileMain from current context (i.e., directory contents and command-line options)

        Precedence: self.file_main > (file specified by opt.fn_main) > (f311's default data file)

        Args:
            opt: FileOptions or None

        Returns:
            FileMain or None
        """
        return self.get_file_generic("main", opt)

    def get_file_abonds(self, opt=None):
        """Analogous to get_file_main()"""
        return self.get_file_generic("abonds", opt)

    def get_file_hmap(self, opt=None):
        """Analogous to get_file_main()"""
        return self.get_file_generic("hmap", opt)

    def get_file_generic(self, name, opt=None):
        """
        Returns new File<sth> object, depending on name

        Args:
            name: string
            opt: FileOptions object
        """
        if opt is None:
            opt = self.__opt
        selfattr = self.__getattribute__("file_"+name)
        if selfattr is not None:
            return selfattr

        optattr = opt.__getattribute__("fn_"+name)
        file_ = getattr(ft, "File"+name.capitalize())()
        if optattr is None:
            file_.load()  # will try to load default file
        else:
            file_.load(optattr)
        return file_

    def get_flprefix(self, _flag_skip_opt=False, opt=None):
        """Returns the prefix for a pfant output file.

        The returned prefix is used to compose a pfant output file name, e.g.
        <prefix>.norm

        Prefix is looked for in the following locations (in this order):
          1) command-line option, i.e., opt.flprefix; if None,
          2) self.file_main.flprefix; if self.file_main is None,
          3) tries to open the main configuration file
        """
        if opt is None:
            opt = self.__opt
        if not _flag_skip_opt and opt.flprefix is not None:
            return opt.flprefix
        if self.file_main is not None:
            return self.file_main.flprefix
        file_ = self.get_file_main()
        return file_.flprefix

    def get_fwhm(self, opt=None):
        """Returns FWHM from command-line option if present, otherwise from main file"""

        if opt is None:
            opt = self.__opt
        if opt.fwhm is not None:
            return opt.fwhm
        if self.file_main is not None:
            return self.file_main.fwhm
        file_ = self.get_file_main()
        return file_.fwhm

    def get_pfant_output_filepath(self, type_="norm"):
        """Returns path to a pfant output filename.

        Args:
          type: "spec", "norm", or "cont"

        Looks for this information in several places; see get_flprefix()
        for more information.
        """
        valid_types = ("spec", "norm", "cont")
        assert type_ in valid_types, "type must be in %s" % (valid_types,)
        return self.get_flprefix()+"."+type_

    def get_nulbad_output_filepath(self):
        """Returns path to nulbad output filename.

        Reproduces nulbad logic in determining its output filename, i.e.,
          1) uses --fn_cv if present; if not,
          2) gets flprefix from main configuration file and adds
             (".norm" or ".spec") + ".nulbad." + <fwhm in 5.3 format>
        """
        if self.__opt.fn_cv is not None:
            filename = self.__opt.fn_cv
        else:
            flprefix = self.get_flprefix()
            # True or None evaluates to "norm"
            ext = ("spec" if self.__opt.norm == False else "norm") + \
                  (".nulbad.{:5.3f}".format(self.get_fwhm()))
            filename = flprefix+"."+ext
        return filename

    def get_fn_modeles(self):
        """Returns name of atmospheric model file."""
        return ft.FileModBin.default_filename if self.__opt.fn_modeles is None \
         else self.__opt.fn_modeles

    def get_fn_molecules(self):
        """Returns name of molecular lines file"""
        return ft.FileMolecules.default_filename if self.__opt.fn_molecules is None \
         else self.__opt.fn_molecules

    def get_args(self):
        """
        Returns a list of command-line arguments (only options that have been set)
        """
        return self.__opt.get_args()

    def rename_outputs(self, sequence, opt=None, sid=None):
        """
        Adds session dir to names of files that will be created by any of the
        executables. To be called *before* create_data_files

        Args:
          sequence: list containing one or more i_* values such as innewmarcs etc

        Note: in order to link pfant->nulbad correctly,
              nulbad "--fn_flux" option will not be used.
        """
        self.__rename_outputs(sequence, opt, sid)


    def __create_data_files(self):
        """
        Creates files for all self.file_* that are not None.

        Corresponding self.opt.fn_xxxx will be overwritten.
        """
        for attr_name in dir(self):
            if attr_name.startswith("file_"):
                obj = self.__getattribute__(attr_name)

                if obj is not None:
                    assert isinstance(obj, ft.DataFile)
                    fn_attr_name = "fn_"+attr_name[5:]
                    curr_fn = self.__opt.__getattribute__(fn_attr_name)
                    # Tries to preserve custom file name given to file
                    # (file name only, not directories)
                    base_fn = os.path.basename(curr_fn) if curr_fn \
                     else obj.default_filename
                    new_fn = self.__sid.join_with_session_dir(base_fn)
                    # Saves file
                    obj.save_as(new_fn)
                    # Overwrites config option
                    self.__opt.__setattr__("fn_"+attr_name[5:], new_fn)

    def __rename_outputs(self, sequence, opt=None, sid=None):
        if opt is None:
            opt = self.__opt
        if sid is None:
            sid = self.__sid
        if FOR_INNEWMARCS in sequence:
            # # innewmarcs -> (hydro2, pfant)
            opt.fn_modeles = sid.join_with_session_dir(
             os.path.basename(opt.fn_modeles) if opt.fn_modeles is not None
             else ft.FileModBin.default_filename)
            opt.fn_opa = sid.join_with_session_dir(
             os.path.basename(opt.fn_opa) if opt.fn_opa is not None
             else ft.FileOpa.default_filename)

        if FOR_HYDRO2 in sequence:
            # # hydro2 -> pfant
            # Task here is to add session_dir to all hydrogen lines filenames, e.g.,
            # if it was "thalpha" it will be something like "session123456/thalpha"

            if not self.file_hmap:
                # if self doesn't have a Hmap object, will load from file
                o = self.file_hmap = ft.FileHmap()
                fn = opt.fn_hmap if opt.fn_hmap is not None else \
                 ft.FileHmap.default_filename
                o.load(fn)
            else:
                o = self.file_hmap
            for row in o.rows:
                # directory/filename is put between single quotes.
                #
                # Fortran reads this correctly. If not put between quotes, Fortran thinks that the "/"
                # denotes the end of the string.
                row.fn = "'"+sid.join_with_session_dir(row.fn)+"'"
                # Done! new hmap file will be created by create_data_files

        # ** pfant -> nulbad
        if FOR_PFANT in sequence or FOR_NULBAD in sequence:
            flprefix = self.get_flprefix(opt=opt)
            opt.flprefix = sid.join_with_session_dir(flprefix)

        if FOR_NULBAD in sequence:
            opt.fn_flux = None  # will cause nulbad to use flprefix
            if opt.fn_cv:
                # Note that this is recursive, but Combo is meant to be
                # run only once.
                opt.fn_cv = sid.join_with_session_dir(opt.fn_cv)


__conf_id_maker = None

def _conf_id_maker():
    """Returns internal ID maker"""
    global __conf_id_maker
    if __conf_id_maker is None:
        __conf_id_maker = IdMaker()
    return __conf_id_maker

