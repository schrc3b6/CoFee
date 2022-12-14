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

void NetdbCheck::registerMatchers(MatchFinder *Finder) {
  // FIXME: Add matchers.
  Finder->addMatcher(
      callExpr(
          callee(
              functionDecl(hasAnyName("::gethostbyname", "::gethostbyaddr", "::hstrerror", "::herror"))
                  .bind("func")))
          .bind("expr"),
      this);
}

void NetdbCheck::check(const MatchFinder::MatchResult &Result) {
  // FIXME: Add callback implementation.
  const auto *Call = Result.Nodes.getNodeAs<CallExpr>("expr");
  const FunctionDecl *FuncDecl = Result.Nodes.getNodeAs<FunctionDecl>("func"); 
  diag(Call->getBeginLoc(), "Function %0 is obsolete, see man %0 for recommended functions")
      << FuncDecl;
}

} // namespace gbr
} // namespace tidy
} // namespace clang
