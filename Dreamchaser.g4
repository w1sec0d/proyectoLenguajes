grammar Dreamchaser;

// Reglas del parser
program: (NEWLINE | statement)* EOF;

statement:
	importStatement
	| constStatement
	| assignmentStatement
	| conditionalStatement
	| whileStatement
	| functionDefinition
	| returnStatement
	| functionCall NEWLINE
	| COMMENT NEWLINE?;

importStatement: 'importar' STRING NEWLINE;
constStatement: 'const' ID (EQUALS)? literal NEWLINE;
assignmentStatement: ID EQUALS expression NEWLINE;

conditionalStatement:
	'si' expression (COMMENT)? NEWLINE block (
		'sino' (expression)? (COMMENT)? NEWLINE block
	)?;

whileStatement: 'mientras' expression NEWLINE block;

functionDefinition:
	'funcion' ID '(' paramList? ')' NEWLINE block;
paramList: ID (',' ID)*;
returnStatement: 'retornar' expression NEWLINE;

functionCall: ID '(' argList? ')';
argList: expression (',' expression)*;

block: statement+;

expression:
	literal																	# LiteralExpr
	| ID																	# IdentifierExpr
	| functionCall															# FunctionCallExpr
	| '(' expression ')'													# ParenExpr
	| expression op = ('*' | '/' | '//' | '%') expression					# MulDivExpr
	| expression op = ('+' | '-') expression								# AddSubExpr
	| expression op = ('==' | '!=' | '>' | '<' | '>=' | '<=') expression	# RelationalExpr;

literal:
	NUMBER		# NumberLiteral
	| STRING	# StringLiteral
	| BOOLEAN	# BooleanLiteral;

// Reglas del lexer
BOOLEAN: 'verdadero' | 'falso';
ID: [a-zA-Z_][a-zA-Z0-9_]*;
NUMBER: INT ('.' [0-9]*)? (('e' | 'E') ('+' | '-')? [0-9]+)?;
fragment INT: [0-9]+;
STRING: '\'' (~[\r\n'])* '\'';

EQUALS: '=';
PLUS: '+';
MINUS: '-';
MULTIPLY: '*';
DIVIDE: '/';
INT_DIVIDE: '//';
MODULO: '%';
EQ: '==';
NEQ: '!=';
GT: '>';
LT: '<';
GTE: '>=';
LTE: '<=';
LPAREN: '(';
RPAREN: ')';

COMMENT: '#' ~[\r\n]*;
NEWLINE: '\r'? '\n';
WS: [ \t]+ -> skip;