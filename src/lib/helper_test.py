# python3
import math

import numpy as np

from src.lib import helper
from src.lib import ops
from src.lib import state

from absl.testing import absltest

class HelpersTest(absltest.TestCase):

  def test_bits_converstions(self):
    bits = helper.val2bits(6, 3)
    self.assertEqual(bits, [1, 1, 0])

    val = helper.bits2val(bits)
    self.assertEqual(val, 6)

  def test_angles(self):
    angle = helper.to_deg(math.pi)
    rad = helper.to_rad(angle)
    self.assertTrue(math.isclose(rad, math.pi))

  def test_density_to_cartesian(self):
    """Test density to cartesian conversion."""

    q0 = state.zeros(1)
    rho = q0.density()
    x, y, z = helper.density_to_cartesian(rho)
    self.assertEqual(x, 0.0)
    self.assertEqual(y, 0.0)
    self.assertEqual(z, 1.0)

    q1 = state.ones(1)
    rho = q1.density()
    x, y, z = helper.density_to_cartesian(rho)
    self.assertEqual(x, 0.0)
    self.assertEqual(y, 0.0)
    self.assertEqual(z, -1.0)

    qh = ops.Hadamard()(q0)
    rho = qh.density()
    x, y, z = helper.density_to_cartesian(rho)
    self.assertTrue(math.isclose(np.real(x), 1.0, abs_tol=1e-6))
    self.assertTrue(math.isclose(np.real(y), 0.0))
    self.assertTrue(math.isclose(np.real(z), 0.0, abs_tol=1e-6))

    qr = ops.RotationZ(90.0 * math.pi / 180.0)(qh)
    rho = qr.density()
    x, y, z = helper.density_to_cartesian(rho)
    self.assertTrue(math.isclose(np.real(x), 0.0, abs_tol=1e-6))
    self.assertTrue(math.isclose(np.real(y), -1.0, abs_tol=1e-6))
    self.assertTrue(math.isclose(np.real(z), 0.0, abs_tol=1e-6))

  def test_frac(self):
    self.assertEqual(helper.bits2frac((0,), 1), 0)
    self.assertEqual(helper.bits2frac((1,), 1), 0.5)
    self.assertEqual(helper.bits2frac((0, 1), 2), 0.25)
    self.assertEqual(helper.bits2frac((1, 0), 2), 0.5)
    self.assertEqual(helper.bits2frac((1, 1), 2), 0.75)

if __name__ == '__main__':
  absltest.main()
