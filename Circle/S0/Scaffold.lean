import Circle.Common.Scaffold

namespace Circle.S0

inductive Sign
  | neg
  | pos
deriving DecidableEq, Repr

def antipode : Sign -> Sign
  | Sign.neg => Sign.pos
  | Sign.pos => Sign.neg

end Circle.S0

