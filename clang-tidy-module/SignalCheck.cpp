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

void SignalCheck::registerMatchers(MatchFinder *Finder) {
  // FIXME: Add matchers.
  Finder->addMatcher(
      callExpr(
          callee(
              functionDecl(hasName("::signal"))
                  .bind("func")))
          .bind("expr"),
      this);
}

void SignalCheck::check(const MatchFinder::MatchResult &Result) {
  // FIXME: Add callback implementation.
  const auto *Call = Result.Nodes.getNodeAs<CallExpr>("expr");
  const FunctionDecl *FuncDecl = Result.Nodes.getNodeAs<FunctionDecl>("func"); 
  diag(Call->getBeginLoc(), "Function %0 is obsolete, use sigaction instead. See man 2 sigaction")
      << FuncDecl;
}

} // namespace gbr
} // namespace tidy
} // namespace clang
