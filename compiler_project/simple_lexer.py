import re
from typing import List
from dataclasses import dataclass

@dataclass
class Token:
    type: str      # Like "KEYWORD_IF", "NUMBER", "IDENTIFIER"
    value: str     # The actual text like "if", "42", "variable"
    line: int      # Line number in code
    column: int    # Column number in code
    filename: str  # File name

class SimpleRegexLexer:
    def __init__(self, problem_tracker):
        self.problem_tracker = problem_tracker
        self.tokens = []
        
    # ALL REGEX PATTERNS IN ONE PLACE - EASY TO UNDERSTAND
        self.patterns = {
            # Comments (C/C++ style)
            'COMMENT': r'//.*|/\*[\s\S]*?\*/',

            # Standard Library Includes
            'STANDARD_LIBRARY': r'^\s*#\s*include\s*<[^>]+>',

            # Own / Project Includes
            'OWN_LIBRARY': r'^\s*#\s*include\s*"[^"]+"',

            # Preprocessor Directives
            'PREPROCESSOR': r'^\s*#\s*(define|undef|ifdef|ifndef|endif|pragma|error|warning|elif|else)\b.*$',
            
            # STRINGS & CHARACTERS
            'STRING': r'"(?:\\.|[^"\\])*"',
            'CHAR': r"'(?:\\.|[^'\\])'",
            
            # NUMBERS
            'HEX_NUMBER': r'0[xX][0-9a-fA-F]+',      # 0x1A3F
            'BINARY_NUMBER': r'0[bB][01]+',          # 0b1010
            'FLOAT_NUMBER': r'(?:\d*\.\d+|\d+\.\d*)(?:[eE][-+]?\d+)?', # 3.14, 2e10
            'OCTAL_NUMBER': r'0[0-7]+',              # 0777
            'INT_NUMBER': r'\d+',                    # 42
            
            # KEYWORDS (Reserved words)
            'KEYWORD': r'\b(if|else|for|while|do|return|class|using|struct|public|namespace|private|protected|static|const|virtual|new|delete|sizeof)\b',
            
            # TYPES (Data types)
            'TYPE': r'\b(int|float|double|char|void|bool|long|short|signed|unsigned)\b',
            
            # SPECIAL VALUES
            'BOOLEAN': r'\b(true|false)\b',
            'NULL': r'\b(nullptr|NULL)\b',
            
            # OPERATORS (2-character first, then 1-character)
            'OPERATOR_2CHAR': r'\+\+|--|->|::|<<|>>|<=|>=|==|!=|&&|\|\||\+=|-=|\*=|\/=|%=',
            'OPERATOR_1CHAR': r'[+\-*/%=<>!&|~^]',
            
            # SYMBOLS
            'SYMBOL': r'[{}()\[\];,.:?]',
            
            # IDENTIFIERS (Variable/function names)
            'IDENTIFIER': r'[a-zA-Z_]\w*',
            
            # NAMESPACE 
            'NAMESPACE': r'\w+::\w+',
            
            # WHITESPACE (to skip)
            'WHITESPACE': r'\s+',

   
        }
        
    # COMBINE ALL PATTERNS INTO ONE BIG REGEX 
        self.master_regex = re.compile(
            '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.patterns.items()),
            re.MULTILINE
        )

    def tokenize(self, code: str, filename: str = "input.txt") -> List[Token]:
        """MAIN FUNCTION - Convert code into tokens"""
        self.tokens = []
        line_num = 1
        line_start = 0
        
        # Find all line starts for accurate line/column numbers
        line_starts = [0]
        for i, char in enumerate(code):
            if char == '\n':
                line_starts.append(i + 1)
        
        # Find all tokens using regex
        for match in self.master_regex.finditer(code):
            token_type = match.lastgroup
            value = match.group()
            start_pos = match.start()
            
            # Calculate line and column
            line_num = 1
            while line_num < len(line_starts) and line_starts[line_num] <= start_pos:
                line_num += 1
            
            current_line_start = line_starts[line_num - 1]
            column_num = start_pos - current_line_start + 1
            
            # Skip whitespace 
            if token_type == 'WHITESPACE':
                continue
                
            # Create token and check for problems
            token = Token(token_type, value, line_num, column_num, filename)
            self.tokens.append(token)
            
            # Check for coding problems
            self.find_problems(token, value)
        
        # Combine function calls after basic tokenization
        self.tokens = self.combine_function_calls(self.tokens)
        
        return self.tokens

    def find_problems(self, token: Token, value: str):
        """Find potential problems in code"""
        
        # Allowed libraries
        allowed_libs = {'iostream', 'stl_library.py', 'stdio.h'}
        
        # Restricted functions 
        restricted_funcs = {
            'printf': 'STLLibrary.printf()', 
            'scanf': 'STLLibrary.scanf()',
            'malloc': 'STLLibrary.malloc()', 
            'free': 'STLLibrary.free()'
        }

        # 1. Check library includes
        if token.type == 'PREPROCESSOR' and 'include' in value:
            lib_match = re.search(r'[<"]([^>"]+)[>"]', value)
            if lib_match:
                lib = lib_match.group(1)
                if lib not in allowed_libs:
                    self.problem_tracker.add_problem(
                        token.line,
                        f"Unauthorized library: {lib}",
                        f"Allowed: {', '.join(allowed_libs)}"
                    )

        # 2. Check macros
        elif token.type == 'PREPROCESSOR' and 'define' in value:
            if '(' in value:
                self.problem_tracker.add_problem(
                    token.line,
                    f"Function-like macro: {value}",
                    "Use constexpr functions instead"
                )
            else:
                self.problem_tracker.add_problem(
                    token.line,
                    f"Constant macro: {value}",
                    "Use constexpr variables instead"
                )

        # 3. Check restricted function calls
        elif token.type == 'IDENTIFIER' and '(' in value:
            func_name = value.split('(')[0]
            if func_name in restricted_funcs:
                self.problem_tracker.add_problem(
                    token.line,
                    f"Direct call to {func_name}()",
                    f"Use {restricted_funcs[func_name]} instead"
                )

        # 4. Check std:: usage
        elif token.type == 'NAMESPACE' and 'std::' in value:
            algo_name = value.split('::')[-1]
            self.problem_tracker.add_problem(
                token.line,
                f"Using std::{algo_name}",
                f"Learning: Create your own {algo_name} implementation"
            )

    def combine_function_calls(self, tokens: List[Token]) -> List[Token]:
        """Combine identifier + parentheses into FUNCTION_CALL tokens"""
        combined = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Check for function call pattern: IDENTIFIER followed by SYMBOL '('
            if (token.type == "IDENTIFIER" and 
                i + 1 < len(tokens) and 
                tokens[i+1].type == "SYMBOL" and 
                tokens[i+1].value == "("):
                
                func_name = token.value
                call_tokens = [token.value]
                start_line = token.line
                start_column = token.column
                
                # Add the opening parenthesis
                call_tokens.append(tokens[i+1].value)
                i += 2  # Move past identifier and '('
                
                # Collect all tokens inside parentheses
                paren_count = 1  # We already have one opening parenthesis
                while i < len(tokens) and paren_count > 0:
                    current_token = tokens[i]
                    call_tokens.append(current_token.value)
                    
                    if current_token.value == "(":
                        paren_count += 1
                    elif current_token.value == ")":
                        paren_count -= 1
                    
                    i += 1
                
                # Create combined FUNCTION_CALL token
                combined.append(Token(
                    type="FUNCTION_CALL",
                    value="".join(call_tokens),
                    line=start_line,
                    column=start_column,
                    filename=token.filename
                ))
            else:
                combined.append(token)
                i += 1
        
        return combined