//===--- NetdbCheck.cpp - clang-tidy --------------------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "GBRChecks.h"
#include <clang/AST/ASTContext.h>
#include <clang/ASTMatchers/ASTMatchFinder.h>

using namespace clang::ast_matchers;

namespace clang {
namespace tidy {
namespace gbr {

void WRSRCheck::registerMatchers(MatchFinder *Finder) {
  // FIXME: Add matchers.
  Finder->addMatcher(
      callExpr(callee(functionDecl(hasAnyName("read", "recv")).bind("func")),
               unless(hasAncestor(mapAnyOf(whileStmt, forStmt, doStmt))))
          .bind("expr"),
      this);
}

void WRSRCheck::check(const MatchFinder::MatchResult &Result) {
  // FIXME: Add callback implementation.
  const auto *Call = Result.Nodes.getNodeAs<CallExpr>("expr");
  const FunctionDecl *FuncDecl = Result.Nodes.getNodeAs<FunctionDecl>("func");
  diag(Call->getBeginLoc(),
       "Function %0 should be called in a loop since not all characters might "
       "have been read. See man %0. If you are sure all characters are handled "
       "this can be ignored.")
      << FuncDecl;
}

} // namespace gbr
} // namespace tidy
} // namespace clang
