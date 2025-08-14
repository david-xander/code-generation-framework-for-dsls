# Generated from alloy.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .alloyParser import alloyParser
else:
    from alloyParser import alloyParser

# This class defines a complete generic visitor for a parse tree produced by alloyParser.

class alloyVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by alloyParser#alloyModule.
    def visitAlloyModule(self, ctx:alloyParser.AlloyModuleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#moduleDecl.
    def visitModuleDecl(self, ctx:alloyParser.ModuleDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#import_.
    def visitImport_(self, ctx:alloyParser.Import_Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#paragraph.
    def visitParagraph(self, ctx:alloyParser.ParagraphContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#sigDecl.
    def visitSigDecl(self, ctx:alloyParser.SigDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#sigExt.
    def visitSigExt(self, ctx:alloyParser.SigExtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#mult.
    def visitMult(self, ctx:alloyParser.MultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#decl.
    def visitDecl(self, ctx:alloyParser.DeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#factDecl.
    def visitFactDecl(self, ctx:alloyParser.FactDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#predDecl.
    def visitPredDecl(self, ctx:alloyParser.PredDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#funDecl.
    def visitFunDecl(self, ctx:alloyParser.FunDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#paraDecls.
    def visitParaDecls(self, ctx:alloyParser.ParaDeclsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#assertDecl.
    def visitAssertDecl(self, ctx:alloyParser.AssertDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#cmdDecl.
    def visitCmdDecl(self, ctx:alloyParser.CmdDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#scope.
    def visitScope(self, ctx:alloyParser.ScopeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#typescope.
    def visitTypescope(self, ctx:alloyParser.TypescopeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#expr.
    def visitExpr(self, ctx:alloyParser.ExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#const_.
    def visitConst_(self, ctx:alloyParser.Const_Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#unOp.
    def visitUnOp(self, ctx:alloyParser.UnOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#binOp.
    def visitBinOp(self, ctx:alloyParser.BinOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#arrowOp.
    def visitArrowOp(self, ctx:alloyParser.ArrowOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#compareOp.
    def visitCompareOp(self, ctx:alloyParser.CompareOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#letDecl.
    def visitLetDecl(self, ctx:alloyParser.LetDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#block.
    def visitBlock(self, ctx:alloyParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#blockOrBar.
    def visitBlockOrBar(self, ctx:alloyParser.BlockOrBarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#quant.
    def visitQuant(self, ctx:alloyParser.QuantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#qualName.
    def visitQualName(self, ctx:alloyParser.QualNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#name.
    def visitName(self, ctx:alloyParser.NameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by alloyParser#number.
    def visitNumber(self, ctx:alloyParser.NumberContext):
        return self.visitChildren(ctx)



del alloyParser