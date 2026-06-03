import io


class Tee(io.StringIO):
    """
    A custom file-like object that writes to both the original standard output
    and a string buffer in memory. This allows capturing traces while still
    letting the user interact with the terminal (e.g. for human input prompts).
    """

    def __init__(self, original_stdout):
        super().__init__()
        self.original_stdout = original_stdout

    def write(self, string):
        self.original_stdout.write(string)
        return super().write(string)

    def flush(self):
        self.original_stdout.flush()
        super().flush()
