'''
Path Finding using Q-Learning
Author: JN, AAL
'''
import random
import math
import numpy
from random import uniform
from simulation_interface import VehicleTrackSystem
from utils import SimulationError
from qfunc import QFunc

#Simulation Constants
SIMULATION_MAX_TIME = 201
NUM_TORQUE_INCREMENTS = QFunc.MAX_TORQUE/QFunc.TORQUE_INCREMENT
NUM_ANGLE_INCREMENTS = (QFunc.MAX_DELTA_STEERING_ANGLE/QFunc.STEERING_ANGLE_INCREMENT)
    
#Interfaced with QFunc Class
def simRedux():
    
    #Initialize Weights to be persistent
    weights= []    
    for i in range(QFunc.NUM_FEATURES):
        weights.append(uniform(-1.0, 1.0))
    best_reward = 0
    #Run until a crash or a stop 
    for episode in range(SIMULATION_MAX_TIME):
        system = VehicleTrackSystem()
        #Manages all the Q Values
        qfunc = QFunc(weights)
        try:
            #Test different torque and angle combinations to find
            #The best one
            epsilon = 1.0/(episode+1.0)
            steering_angle = 0.0
            while True:
                best_q_val = QFunc.CRASH_PUNISHMENT
                best_torque_multiplier = 0
                best_angle_multplier = 0 
                for torque_multiplier in range(int(-NUM_TORQUE_INCREMENTS), int(NUM_TORQUE_INCREMENTS+1)):
                    
                    test_torque = torque_multiplier*QFunc.TORQUE_INCREMENT
                    
                    for angle_multiplier in range(int(-NUM_ANGLE_INCREMENTS), int(NUM_ANGLE_INCREMENTS+1)):
                        
                        test_angle = steering_angle + (angle_multiplier*QFunc.STEERING_ANGLE_INCREMENT)
                        
                        if test_angle > math.pi:
                            test_angle -= math.pi*2.0
                        if test_angle < -math.pi:
                            test_angle += math.pi*2.0
                        
                        dtheta = QFunc.STEERING_ANGLE_INCREMENT*angle_multiplier
                            
                        test_q, test_features = qfunc.qVal(system, steering_angle, test_torque, test_torque, dtheta)
                        
                        if test_q > best_q_val:
                            
                            best_torque_multiplier = torque_multiplier
                            best_angle_multplier = angle_multiplier
                            best_q_val = test_q
                #Save the value of the best one for weights calculations
                qfunc.q_best.append(best_q_val)
                
                #Test if we should explore new options
                if uniform(0.0,1.0) < epsilon: 
                    best_torque_multiplier = random.randint(int(-NUM_TORQUE_INCREMENTS), int(NUM_TORQUE_INCREMENTS))
                    best_angle_multplier = random.randint(int(-NUM_ANGLE_INCREMENTS), int(NUM_ANGLE_INCREMENTS))
                    
                #Update the steering angle, keeping it bound between +- 2pi for feature calculations
                dtheta = best_angle_multplier*QFunc.STEERING_ANGLE_INCREMENT
                steering_angle+=dtheta
                if steering_angle > math.pi:
                    steering_angle -= math.pi*2
                if steering_angle < -math.pi:
                    steering_angle += math.pi*2
                torque = QFunc.TORQUE_INCREMENT*best_torque_multiplier
                
                #Add values found to appropriate places
                q, features = qfunc.qVal(system, steering_angle, torque, torque, dtheta)
                qfunc.q_used.append(q)
                qfunc.feature_evaluations.append(features)
                qfunc.rewards.append(qfunc.reward(system))
                
                system.tick_simulation(front_wheel_torque=torque,
                                               rear_wheel_torque=torque,
                                               steering_angle=steering_angle)                       
        except SimulationError :
            print "Last Reward: ", qfunc.rewards[-1]
            
            last_reward = qfunc.reward(system)
            qfunc.rewards.append(last_reward)
            qfunc.q_best.append(last_reward)
            qfunc.q_used.append(last_reward)
            
            print "Simulation Crash ", episode, " weights: " , weights
            weights = qfunc.update_weights()
            
            if qfunc.rewards[-2] > best_reward:
                system.plot_history()
                best_reward = qfunc.rewards[-2]
            elif episode%20==0:
                system.plot_history()
            elif qfunc.rewards[-2] > 500:
                system.plot_history()
        except WindowsError:
            print "Speed: ", system.speed
            print "Last Reward: ", qfunc.rewards[-1]
            last_reward = qfunc.reward(system)
            qfunc.rewards.append(last_reward)
            qfunc.q_best.append(last_reward)
            qfunc.q_used.append(last_reward)

            print "Simulation Low V", episode, " weights: " , weights
            weights = qfunc.update_weights()
            
            if qfunc.rewards[-2] > best_reward:
                system.plot_history()
                best_reward = qfunc.rewards[-2]
            elif episode%20==0:
                system.plot_history()
            elif qfunc.rewards[-2] > 500:
                system.plot_history()

                              
def main():
    simRedux()
 
if __name__ == "__main__":
    main()
