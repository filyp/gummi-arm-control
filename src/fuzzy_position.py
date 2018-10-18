import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt
from skfuzzy import control as ctrl


current1 = ctrl.Antecedent(np.arange(0, 32, .1), 'current1')
current2 = ctrl.Antecedent(np.arange(0, 32, .1), 'current2')
stiffness = ctrl.Antecedent(np.arange(0, 32, .1), 'stiffness')
displacement = ctrl.Consequent(np.arange(0, 32, .1), 'displacement')

current1.automf(3, 'quant')
current2.automf(3, 'quant')
stiffness.automf(5, 'quant')
displacement.automf(5, 'quant')

# displacement.view()

rule1 = ctrl.Rule(current1['low'] & current2['high'] & stiffness['average'],
                  displacement['lower'])

rule2 = ctrl.Rule((current1['low'] & current2['average'] & stiffness['low']) |
                  (current1['average'] & current2['high'] & stiffness['high']),
                  displacement['low'])

rule3 = ctrl.Rule((current1['low'] & current2['low'] & stiffness['lower']) |
                  (current1['average'] & current2['average'] & stiffness['average']) |
                  (current1['high'] & current2['high'] & stiffness['higher']),
                  displacement['average'])

rule4 = ctrl.Rule((current1['average'] & current2['low'] & stiffness['low']) |
                  (current1['high'] & current2['average'] & stiffness['high']),
                  displacement['high'])

rule5 = ctrl.Rule((current1['high'] & current2['low'] & stiffness['average']),
                  displacement['higher'])


displacement_system = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5])
displacement_comp = ctrl.ControlSystemSimulation(displacement_system)

displacement_comp.input['current1'] = 15
displacement_comp.input['current2'] = 4
displacement_comp.input['stiffness'] = 12
displacement_comp.compute()
displacement.view(sim=displacement_comp)
print(displacement_comp.output)

plt.show()

