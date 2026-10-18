class AddressError(LookupError):
    pass


def redirect_output(cmd, name):
    return f"{cmd} > {name}.out 2>> {name}.err"


class Workload:
    name = ""
    help = ""

    def add_args(self, parser):
        pass

    def validate(self, args, error):
        pass

    def disk(self, args):
        """Suffix of the cheribsd-<arch>-<suffix>.img disk image."""
        raise NotImplementedError

    def label(self, args):
        """Base name for the BBV file and full traces."""
        raise NotImplementedError

    def output_name(self, args):
        return self.label(args)

    def descriptor(self, args):
        """Prefix for per-simpoint trace files."""
        raise NotImplementedError

    def addresses(self, args):
        """(start, end) PCs; end may be None. Raise AddressError if unknown."""
        raise NotImplementedError

    def commands(self, args):
        """List of (working_dir or None, shell command) to run in the guest."""
        raise NotImplementedError

    def info(self, args):
        return {}
