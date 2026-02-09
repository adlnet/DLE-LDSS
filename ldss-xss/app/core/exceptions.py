class MissingColumnsError(Exception):
    def __init__(self, missing_columns, *args):
        super().__init__(missing_columns, *args)
        self.missing_columns=missing_columns
        

class MissingRowsError(Exception):
    def __init__(self, missing_rows, *args):
        super().__init__(missing_rows, *args)
        self.missing_rows = missing_rows

class TermCreationError(Exception):
    pass
