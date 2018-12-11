# The recipe gives simple implementation of a Discrete Proportional-Integral-Derivative
# (PID) controller. PID controller gives output value for error between desired reference
# input and measurement feedback to minimize error value.
#
# https://github.com/ivmech/ivPID
# cnr437@gmail.com
#



class PID:
    """
	Discrete PID control
	"""

    def __init__(self, P, I, D, Derivator=0, Integrator=0, Integrator_max=500, Integrator_min=-500):

        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.Derivator = Derivator
        self.Integrator = Integrator
        self.Integrator_max = Integrator_max
        self.Integrator_min = Integrator_min

        self.set_point = 0.0
        self.error = 0.0

    def update(self, current_value):
        """
		Calculate PID output value for given reference input and feedback
		"""

        self.error = self.set_point - current_value

        P_value = self.Kp * self.error
        D_value = self.Kd * (self.error - self.Derivator)
        self.Derivator = self.error

        self.Integrator = self.Integrator + self.error

        if self.Integrator > self.Integrator_max:
            self.Integrator = self.Integrator_max
        elif self.Integrator < self.Integrator_min:
            self.Integrator = self.Integrator_min

        I_value = self.Integrator * self.Ki

        PID = P_value + I_value + D_value

        return PID

    def set_point(self, set_point):
        """
		Initilize the setpoint of PID
		"""

        self.set_point = set_point
        self.Integrator = 0
        self.Derivator = 0

    def set_integrator(self, Integrator):
        self.Integrator = Integrator

    def set_derivator(self, Derivator):
        self.Derivator = Derivator

    def set_kp(self, P):
        self.Kp = P

    def setKi(self, I):
        self.Ki = I

    def setKd(self, D):
        self.Kd = D

    def getPoint(self):
        return self.set_point

    def getError(self):
        return self.error

    def getIntegrator(self):
        return self.Integrator

    def getDerivator(self):
        return self.Derivator
