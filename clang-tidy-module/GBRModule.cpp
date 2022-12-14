#include <ClangTidy.h>
#include <ClangTidyModule.h>
#include <ClangTidyModuleRegistry.h>
#include "GBRChecks.h"

using namespace clang::ast_matchers;

namespace clang {
namespace tidy {
namespace gbr {

class GBRModule : public ClangTidyModule {
public:
  void addCheckFactories(ClangTidyCheckFactories &CheckFactories) override {
    CheckFactories.registerCheck<NetdbCheck>("modernize-netdb");
    CheckFactories.registerCheck<SignalCheck>("modernize-signal");
    CheckFactories.registerCheck<WRSRCheck>("bugprone-netio");
  }
};

// Register the GBRTidyModule using this statically initialized variable.
static ClangTidyModuleRegistry::Add<GBRModule> X("gbr-module",
                                                       "Add gbr checks.");

} // namespace gbr

// This anchor is used to force the linker to link in the generated object file
// and thus register the GBRModule.
volatile int GBRModuleAnchorSource = 0;

} // namespace tidy
} // namespace clang
