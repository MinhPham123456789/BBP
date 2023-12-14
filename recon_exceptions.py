class NotInstalledError(Exception):
    """Exception raised when nmap is not installed"""
    
    def __init__(self, message="Nmap is either not installed or we couldn't locate nmap path Please ensure nmap is installed"):
        self.message = message 
        super().__init__(message)
        
class ParserError(Exception):
    """Exception raised when we can't parse the output"""
    
    def __init__(self, message="Unable to parse xml output"):
        self.message = message 
        super().__init__(message)

class ExecutionError(Exception):
    """Exception raised when en error occurred during nmap call"""