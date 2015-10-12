import logging

class TableParser:
    """A class which parses a table using BS4 and calls the given functions while parsing

    The purpose of this class is to provide a foolproof method for parsing tables
    that can be used multiple times without cluttering the rest of the parse code.

    This could later provide comprehensive logging of all parsing of tables.
    """
    def __init__(self):
        pass
    def parse_with(self,soup):
        for tableElement in soup.children:

            logging.debug("Parsing tableElement: " + str(tableElement.name))

            # if there is a tbody element, that's where we need to be
            if tableElement.name == "tbody":
                self.parse_with(tableElement)
            # if it is a table row
            elif tableElement.name == "tr":
                self.parse_with(tableElement)
            # if it is a table header
            elif tableElement.name == "th":
                logging.debug("TABLE HEADER")
                self.parse_header(tableElement)
            # if a loose table cell (this shouldn't happen)
            elif tableElement.name == "td":
                self.parse_cell(tableElement)
    # Set the triggers
    def on_parse_header(self,func):
        self.parse_header = func
    def on_parse_cell(self,func):
        self.parse_cell = func
    # default empty functions
    def parse_header(self,soup):
        print("Oops!")
    def parse_cell(self,soup):
        print("Oops!")
