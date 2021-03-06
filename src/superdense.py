# python3
"""Example: Superdense Coding."""

import math

from absl import app

from src.lib import bell
from src.lib import ops


def alice_manipulates(psi, bit0, bit1):
  """Alice encodes 2 classical bits in her 1 qubit."""

  ret = ops.Identity(2)(psi)
  if bit0:
    ret = ops.PauliZ()(ret)
  if bit1:
    ret = ops.PauliX()(ret)
  return ret


def bob_measures(psi, expect0, expect1):
  """Bob measures both bits (in computational basis)."""

  # Change Hadamard basis back to computational basis.
  psi = ops.Cnot(0, 1)(psi)
  psi = ops.Hadamard(1)(psi)

  p0, _ = ops.Measure(psi, 0, tostate=expect0)
  p1, _ = ops.Measure(psi, 1, tostate=expect1)

  if (not math.isclose(p0, 1.0, abs_tol=1e-6) or
      not math.isclose(p1, 1.0, abs_tol=1e-6)):
    raise AssertionError(f'Invalid Result p0 {p0} p1 {p1}')

  print(f'Expected/matched: |{expect0}{expect1}>')


def main(argv):
  if len(argv) > 1:
    raise app.UsageError('Too many command-line arguments.')

  # Step 1: Alice and Bob share an entangled pair and physically separate.
  psi = bell.bell_state(0, 0)

  # Alices manipulates her qubit and sends her 1 qubit back to Bob,
  # who measures. In the Hadamard basis he would get b00, b01, etc
  # but we're measuring in the computational basis by reverse
  # applying Hadamard and Cnot.
  for bit0 in range(2):
    for bit1 in range(2):
      psi_alice = alice_manipulates(psi, bit0, bit1)
      bob_measures(psi_alice, bit0, bit1)


if __name__ == '__main__':
  app.run(main)