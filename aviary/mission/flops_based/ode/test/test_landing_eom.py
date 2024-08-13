import unittest

import numpy as np
import openmdao.api as om
from openmdao.utils.assert_utils import (assert_check_partials,
                                         assert_near_equal)

from aviary.mission.flops_based.ode.landing_eom import (
    FlareEOM, GlideSlopeForces, FlareSumForces, GroundSumForces)
from aviary.models.N3CC.N3CC_data import (
    detailed_landing_flare, inputs)
from aviary.validation_cases.validation_tests import do_validation_test
from aviary.variable_info.variables import Dynamic


class FlareEOMTest(unittest.TestCase):
    def test_case(self):
        prob = om.Problem()

        time, _ = detailed_landing_flare.get_item('time')
        nn = len(time)
        aviary_options = inputs

        prob.model.add_subsystem(
            "landing_flare_eom",
            FlareEOM(num_nodes=nn, aviary_options=aviary_options),
            promotes_inputs=['*'],
            promotes_outputs=['*'])

        prob.setup(check=False, force_alloc_complex=True)

        do_validation_test(
            prob,
            'landing_flare_eom',
            input_validation_data=detailed_landing_flare,
            output_validation_data=detailed_landing_flare,
            input_keys=[
                'angle_of_attack',
                Dynamic.Mission.FLIGHT_PATH_ANGLE,
                Dynamic.Mission.VELOCITY,
                Dynamic.Mission.MASS,
                Dynamic.Mission.LIFT,
                Dynamic.Mission.THRUST_TOTAL,
                Dynamic.Mission.DRAG],
            output_keys=[
                Dynamic.Mission.DISTANCE_RATE,
                Dynamic.Mission.ALTITUDE_RATE],
            tol=1e-2, atol=1e-8, rtol=5e-10)

    def test_GlideSlopeForces(self):
        """
        test on single component GlideSlopeForces
        """

        tol = 1e-6
        aviary_options = inputs
        prob = om.Problem()
        prob.model.add_subsystem(
            "glide", GlideSlopeForces(num_nodes=2, aviary_options=aviary_options), promotes=["*"]
        )
        prob.model.set_input_defaults(
            Dynamic.Mission.MASS, np.array([106292, 106292]), units="lbm"
        )
        prob.model.set_input_defaults(
            Dynamic.Mission.DRAG, np.array([47447.13138523, 44343.01567596]), units="N"
        )
        prob.model.set_input_defaults(
            Dynamic.Mission.LIFT, np.array([482117.47027692, 568511.57097785]), units="N"
        )
        prob.model.set_input_defaults(
            "angle_of_attack", np.array([5.086, 6.834]), units="deg"
        )
        prob.model.set_input_defaults(
            Dynamic.Mission.FLIGHT_PATH_ANGLE, np.array([-3.0, -2.47]), units="deg"
        )
        prob.setup(check=False, force_alloc_complex=True)
        prob.run_model()

        assert_near_equal(
            prob["forces_perpendicular"], np.array(
                [135087.0, 832087.6]), tol
        )
        assert_near_equal(
            prob["required_thrust"], np.array(
                [-44751.64, -391905.6]), tol
        )

        partial_data = prob.check_partials(out_stream=None, method="cs")
        assert_check_partials(partial_data, atol=1e-8, rtol=1e-12)

    def test_FlareSumForces(self):
        """
        test on single component FlareSumForces
        """

        tol = 1e-6
        aviary_options = inputs
        prob = om.Problem()
        prob.model.add_subsystem(
            "flare", FlareSumForces(num_nodes=2, aviary_options=aviary_options), promotes=["*"]
        )
        prob.model.set_input_defaults(
            Dynamic.Mission.MASS, np.array([106292, 106292]), units="lbm"
        )
        prob.model.set_input_defaults(
            Dynamic.Mission.DRAG, np.array([47447.13138523, 44343.01567596]), units="N"
        )
        prob.model.set_input_defaults(
            Dynamic.Mission.LIFT, np.array([482117.47027692, 568511.57097785]), units="N"
        )
        prob.model.set_input_defaults(
            Dynamic.Mission.THRUST_TOTAL, np.array([4980.3, 4102]), units="N"
        )
        prob.model.set_input_defaults(
            "angle_of_attack", np.array([5.086, 6.834]), units="deg"
        )
        prob.model.set_input_defaults(
            Dynamic.Mission.FLIGHT_PATH_ANGLE, np.array([-3., -2.47]), units="deg"
        )
        prob.setup(check=False, force_alloc_complex=True)
        prob.run_model()

        assert_near_equal(
            prob["forces_horizontal"], np.array(
                [17173.03, 15710.98]), tol
        )
        assert_near_equal(
            prob["forces_vertical"], np.array(
                [11310.84, 97396.16]), tol
        )

        partial_data = prob.check_partials(out_stream=None, method="cs")
        assert_check_partials(partial_data, atol=1e-9, rtol=1e-12)

    def test_GroundSumForces(self):
        """
        test on single component GroundSumForces
        """

        tol = 1e-6
        prob = om.Problem()
        prob.model.add_subsystem(
            "ground", GroundSumForces(num_nodes=2, friction_coefficient=0.025), promotes=["*"]
        )
        prob.model.set_input_defaults(
            Dynamic.Mission.MASS, np.array([106292, 106292]), units="lbm"
        )
        prob.model.set_input_defaults(
            Dynamic.Mission.DRAG, np.array([47447.13138523, 44343.01567596]), units="N"
        )
        prob.model.set_input_defaults(
            Dynamic.Mission.LIFT, np.array([482117.47027692, 568511.57097785]), units="N"
        )
        prob.model.set_input_defaults(
            Dynamic.Mission.THRUST_TOTAL, np.array([4980.3, 4102]), units="N"
        )
        prob.setup(check=False, force_alloc_complex=True)
        prob.run_model()

        assert_near_equal(
            prob["forces_horizontal"], np.array(
                [42466.83, 40241.02]), tol
        )
        assert_near_equal(
            prob["forces_vertical"], np.array(
                [9307.098, 95701.199]), tol
        )

        partial_data = prob.check_partials(out_stream=None, method="cs")
        assert_check_partials(partial_data, atol=1e-12, rtol=1e-12)


if __name__ == "__main__":
    unittest.main()
