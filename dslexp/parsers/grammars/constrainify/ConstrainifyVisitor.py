# Generated from Constrainify.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .ConstrainifyParser import ConstrainifyParser
else:
    from ConstrainifyParser import ConstrainifyParser

# This class defines a complete generic visitor for a parse tree produced by ConstrainifyParser.

class ConstrainifyVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ConstrainifyParser#program.
    def visitProgram(self, ctx:ConstrainifyParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ConstrainifyParser#statement.
    def visitStatement(self, ctx:ConstrainifyParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ConstrainifyParser#contextStm.
    def visitContextStm(self, ctx:ConstrainifyParser.ContextStmContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ConstrainifyParser#propertyDefinition.
    def visitPropertyDefinition(self, ctx:ConstrainifyParser.PropertyDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ConstrainifyParser#propertyType.
    def visitPropertyType(self, ctx:ConstrainifyParser.PropertyTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ConstrainifyParser#constraint.
    def visitConstraint(self, ctx:ConstrainifyParser.ConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ConstrainifyParser#propertyCall.
    def visitPropertyCall(self, ctx:ConstrainifyParser.PropertyCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ConstrainifyParser#invariantStm.
    def visitInvariantStm(self, ctx:ConstrainifyParser.InvariantStmContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ConstrainifyParser#comparator.
    def visitComparator(self, ctx:ConstrainifyParser.ComparatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ConstrainifyParser#value.
    def visitValue(self, ctx:ConstrainifyParser.ValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ConstrainifyParser#operation.
    def visitOperation(self, ctx:ConstrainifyParser.OperationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ConstrainifyParser#operator.
    def visitOperator(self, ctx:ConstrainifyParser.OperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ConstrainifyParser#condition.
    def visitCondition(self, ctx:ConstrainifyParser.ConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ConstrainifyParser#function.
    def visitFunction(self, ctx:ConstrainifyParser.FunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ConstrainifyParser#boolean.
    def visitBoolean(self, ctx:ConstrainifyParser.BooleanContext):
        return self.visitChildren(ctx)



del ConstrainifyParser