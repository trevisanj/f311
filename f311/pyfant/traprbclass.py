from subprocess import Popen, PIPE, STDOUT
import subprocess
from .runnables import Runnable
import a99
import os
from .errors import *


__all__ = ["TRAPRB"]

# TODO dismember with superclass should I want to create another executable, perhaps/probably start new lineage in a99!
class TRAPRB(Runnable):
    """
    Class representing the TRAPRB code [Jarmain&McCallum1970]

    References:

    [Jarmain&McCallum1970] Jarmain, W. R., and J. C. McCallum.
    "TRAPRB: a computer program for molecular transitions." University of Western Ontario (1970)
    """

    def __init__(self):
        Runnable.__init__(self)
        self.exe_path = "fcf"
        self.fn_input = "data.dat"
        self.fn_output = None
        self.flag_log_console = True
        self.flag_log_file = True


    def run(self):
        """Runs executable.

        Blocking routine. Only returns when executable finishes running.
        """
        assert not self._flag_running, "Already running"
        assert not self._flag_finished, "Already finished"
        a99.get_python_logger().debug("Running %s '%s'" % (self.__class__.__name__.lower(), self.name))
        self.__run()

    def __run(self):
        """Called both from run() and run_from_combo()."""

        fn_output = self._get_fn_output()

        # Deletes output file if it already exists so that we don't have TRAPRB failing because of this
        if os.path.isfile(fn_output):
            os.unlink(fn_output)

        # Logging
        if self.flag_log_file:
            log_path = "traprb.log"
            if self.flag_log_console:
                stdout_ = a99.LogTwo(log_path)
            else:
                stdout_ = open(log_path, "w")
        else:
            if self.flag_log_console:
                stdout_ = subprocess.STD_OUTPUT_HANDLE
            else:
                stdout_ = None

        try:
            self._flag_running = True

            self.__popen = subprocess.run([self.exe_path], stdout=PIPE,
                input=bytes("{}\n{}\n".format(self.fn_input, fn_output), "ascii"))

            if stdout_ is not None:
                stdout_.write(self.__popen.stdout.decode("ascii"))

            if self.__popen.returncode != 0:
                raise FailedError("%s failed (returncode=%s)" % (self.__class__.__name__.lower(), self.__popen.returncode))

        except Exception as e:
            flag_re_raise = True
            if self.__popen:
                if isinstance(e, FailedError) and self._flag_killed:
                    # dismisses error if explicitly killed
                    flag_re_raise = False
                elif isinstance(e, IOError) and self.__popen.returncode == 0:
                    # Sometimes a IOError is raised even if Fortran executes
                    # successfully, so the error is dismissed
                    a99.get_python_logger().warning("Harmless error in TRAPRB")
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

            if stdout_ is not None:
                stdout_.close()




    def _get_fn_output(self):
        fn_output = self.fn_input + ".out" if self.fn_output is None else self.fn_output
        return fn_output

    def load_result(self):
        """Stores output in self.result["output"]"""
        import f311.filetypes as ft
        f = ft.FileTRAPRBOutput()
        f.load(self._get_fn_output())
        self.result["output"] = f
