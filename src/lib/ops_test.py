# python3
import math

from absl.testing import absltest

from src.lib import helper
from src.lib import ops
from src.lib import state


class OpsTest(absltest.TestCase):

  def test_id(self):
    identity = ops.Identity()
    self.assertEqual(identity[0, 0], 1)
    self.assertEqual(identity[0, 1], 0)
    self.assertEqual(identity[1, 0], 0)
    self.assertEqual(identity[1, 1], 1)

  def test_unitary(self):
    self.assertTrue(ops.PauliX().is_unitary())
    self.assertTrue(ops.PauliY().is_unitary())
    self.assertTrue(ops.PauliZ().is_unitary())
    self.assertTrue(ops.Identity().is_unitary())

  def test_double_hadamard(self):
    """Check that Hadamard is fully reversible."""

    psi = state.zeros(2)

    psi2 = ops.Hadamard(2)(ops.Hadamard(2)(psi))
    self.assertEqual(psi2.nbits, 2)
    self.assertTrue(psi.is_close(psi2))

    combo = ops.Hadamard(2) @ ops.Hadamard(2)
    psi3 = combo(psi)
    self.assertEqual(psi3.nbits, 2)
    self.assertTrue(psi.is_close(psi3))
    self.assertTrue(psi.density().is_pure())

  def test_cnot(self):
    """Check implementation of ControlledU via Cnot."""

    psi = state.bitstring(0, 1)
    psi2 = ops.Cnot(0, 1)(psi)
    self.assertTrue(psi.is_close(psi2))

    psi2 = ops.Cnot(0, 1)(state.bitstring(1, 1))
    self.assertTrue(psi2.is_close(state.bitstring(1, 0)))

    psi2 = ops.Cnot(0, 3)(state.bitstring(1, 0, 0, 0, 1))
    self.assertTrue(psi2.is_close(state.bitstring(1, 0, 0, 1, 1)))

    psi2 = ops.Cnot(4, 0)(state.bitstring(1, 0, 0, 0, 1))
    self.assertTrue(psi2.is_close(state.bitstring(0, 0, 0, 0, 1)))

  def test_cnot0(self):
    """Check implementation of ControlledU via Cnot0."""

    # Check operator itself.
    x = ops.PauliX() * ops.Identity()
    self.assertTrue(ops.Cnot0(0, 1).
                    is_close(x @ ops.Cnot(0, 1) @ x))

    # Compute simplest case with Cnot0.
    psi = state.bitstring(1, 0)
    psi2 = ops.Cnot0(0, 1)(psi)
    self.assertTrue(psi.is_close(psi2))

    # Compute via explicit constrution.
    psi2 = (x @ ops.Cnot(0, 1) @ x)(psi)
    self.assertTrue(psi.is_close(psi2))

    # Different offsets.
    psi2 = ops.Cnot0(0, 1)(state.bitstring(0, 1))
    self.assertTrue(psi2.is_close(state.bitstring(0, 0)))

    psi2 = ops.Cnot0(0, 3)(state.bitstring(0, 0, 0, 0, 1))
    self.assertTrue(psi2.is_close(state.bitstring(0, 0, 0, 1, 1)))

    psi2 = ops.Cnot0(4, 0)(state.bitstring(1, 0, 0, 0, 0))
    self.assertTrue(psi2.is_close(state.bitstring(0, 0, 0, 0, 0)))

  def test_controlled_controlled(self):
    """Toffoli gate over 4 qubits to verify that controlling works."""

    cnot = ops.Cnot(0, 3)
    toffoli = ops.ControlledU(0, 1, cnot)
    self.assertTrue(toffoli.is_close(ops.Toffoli(0, 1, 4)))

    psi = toffoli(state.bitstring(0, 1, 0, 0, 1))
    self.assertTrue(psi.is_close(state.bitstring(0, 1, 0, 0, 1)))

    psi = toffoli(state.bitstring(1, 1, 0, 0, 1))
    self.assertTrue(psi.is_close(state.bitstring(1, 1, 0, 0, 0)))

    psi = toffoli(state.bitstring(0, 0, 1, 1, 0, 0, 1), idx=2)
    self.assertTrue(psi.is_close(state.bitstring(0, 0, 1, 1, 0, 0, 0)))

  def test_swap(self):
    """Test swap gate, various indices."""

    swap = ops.Swap(0, 4)
    psi = swap(state.bitstring(1, 0, 1, 0, 0))
    self.assertTrue(psi.is_close(state.bitstring(0, 0, 1, 0, 1)))

    swap = ops.Swap(2, 0)
    psi = swap(state.bitstring(1, 0, 0))
    self.assertTrue(psi.is_close(state.bitstring(0, 0, 1)))

    op_manual = ops.Identity()**2 * swap * ops.Identity()
    psi = op_manual(state.bitstring(1, 1, 0, 1, 1, 0))
    self.assertTrue(psi.is_close(state.bitstring(1, 1, 1, 1, 0, 0)))

    psi = swap(state.bitstring(1, 1, 0, 1, 1, 0), idx=2)
    self.assertTrue(psi.is_close(state.bitstring(1, 1, 1, 1, 0, 0)))

  def test_t_gate(self):
    """Test that T^2 == S."""

    t = ops.Tgate()
    self.assertTrue(t(t).is_close(ops.Phase()))

  def test_v_gate(self):
    """Test that V^2 == X."""

    t = ops.Vgate()
    self.assertTrue(t(t).is_close(ops.PauliX()))

  def test_yroot_gate(self):
    """Test that Yroot^2 == Y."""

    t = ops.Yroot()
    self.assertTrue(t(t).is_close(ops.PauliY()))

  def check_rotation(self, angle):
    # Note that RotationZ rotates by theta/2
    psi = ops.RotationZ(math.pi/180.0*angle)(state.zero)
    self.assertTrue(math.isclose(-angle/2, psi.phase(0), abs_tol=1e-5))

  def test_phase(self):
    psi = state.zero
    psi = ops.RotationZ(math.pi/2)(psi)
    phase = psi.phase(0)

    # Note that Rotation rotates by theta/2.
    self.assertTrue(math.isclose(phase, -45.0, abs_tol=1e-6))

    # Test all other angles, check for sign flips.
    for i in range(360):
      self.check_rotation(float(i)/2)
    for i in range(360):
      self.check_rotation(float(-i)/2)

  def test_rk(self):
    rk0 = ops.Rk(0)
    self.assertTrue(rk0.is_close(ops.Identity()))

    rk1 = ops.Rk(1)
    self.assertTrue(rk1.is_close(ops.PauliZ()))

    rk2 = ops.Rk(2)
    self.assertTrue(rk2.is_close(ops.Sgate()))

    rk3 = ops.Rk(3)
    self.assertTrue(rk3.is_close(ops.Tgate()))

    for idx in range(8):
      psi = state.zeros(2)
      psi = (ops.Rk(idx)**2 @ ops.Rk(-idx)**2)(psi)
      self.assertTrue(psi.is_close(state.zeros(2)))

  def test_dft(self):
    """Build 'manually' a 3 qubit gate, Nielsen/Chuang Box 5.1."""

    h = ops.Hadamard()

    op = ops.Identity(3)
    op = op(h, 0)
    op = op(ops.ControlledU(1, 0, ops.Rk(2)), 0)  # S-gate
    op = op(ops.ControlledU(2, 0, ops.Rk(3)), 0)  # T-gate
    op = op(h, 1)
    op = op(ops.ControlledU(1, 0, ops.Rk(2)), 1)  # S-gate
    op = op(h, 2)
    op = op(ops.Swap(0, 2), 0)

    op3 = ops.Qft(3)
    self.assertTrue(op3.is_close(op))

  def test_dft_adjoint(self):
    bits = [0, 1, 0, 1, 1, 0]
    psi = state.bitstring(*bits)
    psi = ops.Qft(6)(psi)
    psi = ops.Qft(6).adjoint()(psi)
    maxbits, _ = psi.maxprob()
    self.assertEqual(maxbits, tuple(bits))

  def test_padding(self):
    ident = ops.Identity(3)
    h = ops.Hadamard()

    op = ident(h, 0)
    op_manual = h * ops.Identity(2)
    self.assertTrue(op.is_close(op_manual))
    op = ident(h, 1)
    op_manual = ops.Identity() * h * ops.Identity()
    self.assertTrue(op.is_close(op_manual))
    op = ident(h, 2)
    op_manual = ops.Identity(2) * h
    self.assertTrue(op.is_close(op_manual))

    ident = ops.Identity(4)
    cx = ops.Cnot(0, 1)

    op = ident(cx, 0)
    op_manual = cx * ops.Identity(2)
    self.assertTrue(op.is_close(op_manual))
    op = ident(cx, 1)
    op_manual = ops.Identity(1) *  cx * ops.Identity(1)
    self.assertTrue(op.is_close(op_manual))
    op = ident(cx, 2)
    op_manual = ops.Identity(2) *  cx
    self.assertTrue(op.is_close(op_manual))

  def test_controlled_rotations(self):
    psi = state.bitstring(1, 1, 1)
    psi02 = ops.ControlledU(0, 2, ops.Rk(1))(psi)
    psi20 = ops.ControlledU(2, 0, ops.Rk(1))(psi)
    self.assertTrue(psi02.is_close(psi20))

  def test_bloch(self):
    psi = state.zeros(1)
    x, y, z = helper.density_to_cartesian(psi.density())
    self.assertEqual(x, 0.0)
    self.assertEqual(y, 0.0)
    self.assertEqual(z, 1.0)

    psi = ops.PauliX()(psi)
    x, y, z = helper.density_to_cartesian(psi.density())
    self.assertEqual(x, 0.0)
    self.assertEqual(y, 0.0)
    self.assertEqual(z, -1.0)

    psi = ops.Hadamard()(psi)
    x, y, z = helper.density_to_cartesian(psi.density())
    self.assertTrue(math.isclose(x, -1.0, abs_tol=1e-6))
    self.assertTrue(math.isclose(y, 0.0, abs_tol=1e-6))
    self.assertTrue(math.isclose(z, 0.0, abs_tol=1e-6))


if __name__ == '__main__':
  absltest.main()
