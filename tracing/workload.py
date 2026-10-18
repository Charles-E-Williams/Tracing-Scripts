from abc import ABC, abstractmethod


def option_name(arg_name):
    return "--" + arg_name.replace("_", "-")


def redirect_output(command, output_name):
    return f"{command} > {output_name}.out 2>> {output_name}.err"


class Workload(ABC):
    name = ""
    help = ""

    def add_args(self, parser):
        pass

    def validate(self, args, report_error):
        pass

    @abstractmethod
    def display_name(self, args):
        """How error messages refer to the selected benchmark."""

    @abstractmethod
    def disk_image_suffix(self, args):
        """Suffix of the cheribsd-<arch>-<suffix>.img disk image."""

    @abstractmethod
    def trace_name(self, args):
        """Base name for the BBV file and full traces."""

    def output_dir_name(self, args):
        return self.trace_name(args)

    @abstractmethod
    def simpoint_trace_prefix(self, args):
        """Prefix for per-simpoint trace files."""

    @abstractmethod
    def start_end_addresses(self, args):
        """(start PC, end PC); either is None when not recorded."""

    @abstractmethod
    def guest_commands(self, args):
        """List of (working_dir or None, shell command) to run in the guest."""

    def info_fields(self, args):
        return {}
