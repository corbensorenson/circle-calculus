import Circle.Common.Scaffold
import Circle.S2.Scaffold

namespace Circle.S3

structure SuspendedSurfaceSpec where
  vertices : Nat
  edges : Nat
  faces : Nat
deriving DecidableEq, Repr

def quaternionTrackName : String :=
  "S3Q"

def hopfTrackName : String :=
  "S3H"

end Circle.S3

