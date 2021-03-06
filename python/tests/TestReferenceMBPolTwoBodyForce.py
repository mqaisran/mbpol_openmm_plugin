from __future__ import print_function

import unittest
from simtk.openmm import app
import simtk.openmm as mm
from simtk import unit
import sys
import mbpol

class TestCustomForce(unittest.TestCase):
    """This tests the Reference implementation of ReferenceMBPolOneBodyForce."""

    def testTwoBody(self, nonbondedMethod=app.CutoffNonPeriodic):
        expected_energy = 6.14207815
        pdb = app.PDBFile("pdb_files/water2.pdb")
        forcefield = app.ForceField("../mbpol.xml") 

        nonbondedCutoff = 10*unit.nanometer
        
        if (nonbondedMethod == app.PME):
            boxDimension = 50
            boxsize = [boxDimension, boxDimension, boxDimension]
            pdb.topology.setUnitCellDimensions( boxsize )
            
        system = forcefield.createSystem(pdb.topology, nonbondedMethod=nonbondedMethod, nonbondedCutoff=nonbondedCutoff)

        #forces must be removed from the system to test single force
        #order of forces:
        # elec
        # one
        # two
        # three
        # CMMotionRemover
        # CustomDispersion
        system.removeForce(0) #remove elec
        system.removeForce(0) #remove one
        system.removeForce(1) #remove three
        system.removeForce(1) #remove CMMotionRemover
        system.removeForce(1) #remove CustomDispersion

        
        integrator = mm.LangevinIntegrator(0.0, 0.1, 0.01)
        platform = mm.Platform.getPlatformByName('Reference')
        simulation = app.Simulation(pdb.topology, system, integrator, platform)
        simulation.context.setPositions(pdb.positions)
        simulation.context.computeVirtualSites()
        state = simulation.context.getState(getForces=True, getEnergy=True, getPositions=True)
        potential_energy = state.getPotentialEnergy()
        potential_energy.in_units_of(unit.kilocalorie_per_mole)
        
        self.assertTrue(abs(potential_energy.in_units_of(unit.kilocalorie_per_mole)._value - expected_energy) < .01)
    


if __name__ == '__main__':
    unittest.main()
