grammar Dreamchaser;

prog: statement* EOF;

statement:
	importStmt
	| constStmt
	| varDecl
	| assignment
	| arithmeticExpr
	| relationalExpr
	| controlStructure
	| functionDecl
	| functionCall
	| printStmt
	| COMMENT
	| NEWLINE;

importStmt: 'importar' STRING;
constStmt: 'const' ID '=' expr;
varDecl: ID '=' expr;
assignment: ID '=' expr;
arithmeticExpr: expr (('*' | '/') expr | ('+' | '-') expr);
relationalExpr:
	expr (('==' | '!=' | '>' | '<' | '>=' | '<=') expr);
controlStructure:
	'si' expr 'retornar' expr ('sino' 'retornar' expr)?
	| 'mientras' expr statement*;
functionDecl: 'funcion' ID '(' paramList? ')' statement*;
functionCall: ID '(' argList? ')';
printStmt: 'imprimir' '(' expr ')';

paramList: ID (',' ID)*;
argList: expr (',' expr)*;

expr: INT | FLOAT | BOOL | STRING | ID | '(' expr ')';

COMMENT: '#' ~[\r\n]*;
NEWLINE: [\r\n]+;
WS: [ \t]+ -> skip;

ID: [a-zA-Z_][a-zA-Z_0-9]*;
INT: [0-9]+;
FLOAT: [0-9]+ '.' [0-9]+;
BOOL: 'verdadero' | 'falso';
STRING: '\'' .*? '\'';