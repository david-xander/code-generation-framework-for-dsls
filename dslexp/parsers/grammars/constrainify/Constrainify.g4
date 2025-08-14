grammar Constrainify;

program : statement+ EOF; // There can be multiple statements
statement : contextStm; // Context statement supported for now

contextStm 
    : '@' IDENTIFIER '{' (propertyDefinition | constraint)+ '}' // A context block like: @Name { properties, constraints }
    ;

propertyDefinition: IDENTIFIER ':' propertyType ';';

propertyType: ('String' | 'Int' | 'Float' | 'Boolean' | 'Date' | '@' IDENTIFIER) ;

constraint 
    : propertyCall invariantStm comparator? operation (condition)? ';' // Constraint with operator and optional value
    | propertyCall 'if' comparator? operation 'then' '{' constraint+ '}' // Restricción anidada
    | propertyCall 'equals' operation 'if' operation 
    ;

propertyCall 
    : (':' IDENTIFIER | function)? ':' IDENTIFIER // Propiedades son identificadores precedidos de ':'
    ;

invariantStm: ('cannot be' | 'must be' | 'must be in');

comparator 
    : ('equals' | '>' |'<' | '>=' | '<=' | '=')
    ;

operation: value operator value | value ;

value 
    : QUOTED_STRING      // Cadenas entre comillas
    | NUMBER             // Números
    | propertyCall     
    | boolean  
    | function
    | 'some' | 'every' | 'none' // Cuantificadores
    | '[' value (',' value)* ']' // Listas de valores
    ;

operator: '+' | '-' | '*' | '/' ;

condition 
    : 'when' propertyCall '=' value // Condiciones con "when"
    ;

function: IDENTIFIER '(' ')';

boolean: 'true' | 'false' ;


// Tokens básicos
IDENTIFIER 
    : [a-zA-Z_][a-zA-Z0-9_]*; // Identificadores válidos (alfa-numéricos)
NUMBER 
    : [0-9]+('.'[0-9]+)?; // Números enteros o decimales
QUOTED_STRING 
    : '"' (~["])* '"'; // Cadenas entre comillas dobles
WS 
    : [ \t\r\n]+ -> skip; // Ignorar espacios en blanco y saltos de línea
COMMENT 
    : '//' ~[\r\n]* -> skip; // Comentarios de una línea
