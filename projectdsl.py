import simpy
import random
import statistics
from tkinter import *
import tkinter as tk
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
import numpy as np

RANDOM_SEED = 42
NUM_DOCTORS = 2
SIM_TIME = 100
NUM_NURSES = 5
NUM_DOCTORS = 4
TREATMENT_TIMES = {'emergency': 20, 'urgent': 10, 'non urgent': 15}
ARRIVAL_RATE =1
TRIAGE_LEVELS = {'emergency': 1, 'urgent': 2, 'non urgent': 3}
PATIENTS=[]

class Patient:
    def __init__(self, id, arrival_time, triage_level, treatment_time, wait_time,age,sex):
        self.id = id
        self.arrival_time = arrival_time
        self.triage_level = triage_level
        self.treatment_time = treatment_time
        self.wait_time = wait_time
        self.age=age
        self.sex=sex
    def info(self,time,i):
        if i==1:
            self.got_doctor=time
        if i==2:
            self.free_doctor=time      

def patient_generator(env,arrival_rate, triage_levels, treatment_times, doctors, doctor_resource):
    i = 0
    while True:
        i=i+1
        yield env.timeout(random.expovariate(1/5))
        arrival_time = env.now
        triage_level = random.choices(list(triage_levels.keys()), weights=[0.2, 0.3, 0.5], k=1)[0]
        treatment_time = treatment_times[triage_level]
        wait_time = 0
        age = int(random.gauss(45, 15))
        sex = random.choice(['male', 'female'])
        patient = Patient(i, arrival_time, triage_level, treatment_time, wait_time,age,sex)
        PATIENTS.append(patient)
        env.process(patient_flow(env, patient, triage_levels, treatment_times, doctors, doctor_resource))        
        inter_arrival_time = random.expovariate(arrival_rate)
        yield env.timeout(inter_arrival_time)
       
def patient_flow(env, patient, triage_levels, treatment_times, doctors, doctor_resource):
    with waiting_room.request() as req:
        start_wait = env.now
        yield req
        end_wait = env.now
        patient.wait_time = end_wait - start_wait
        triage_start_time = env.now
        triage_duration = random.uniform(1, 5)
        yield env.timeout(triage_duration)
        triage_end_time = env.now
        patient.triage_time = triage_end_time - triage_start_time
        if patient.triage_level == 'emergency':
            with emergency_room.request() as req:
                treatment_start_time = env.now
                yield req
                with doctor_resource.request(priority=0) as doctor_req:
                    yield doctor_req
                    patient.info(env.now,1)
                    output_text.insert(END, f"Patient {patient.id} having emergency arrived at hospital at: {int(env.now)} minutes.\n")
                    yield env.timeout(TREATMENT_TIMES['emergency'])
                treatment_end_time = env.now
                patient.info(env.now,1)
                patient.treatment_time = treatment_end_time - treatment_start_time
                patient.total_time = patient.wait_time + patient.triage_time + patient.treatment_time
        elif patient.triage_level == 'urgent':
            with urgent_room.request() as req:
                treatment_start_time = env.now
                yield req
                with doctor_resource.request(priority=1) as doctor_req:
                    yield doctor_req
                    output_text.insert(END, f"Patient {patient.id} having urgent case arrived at hospital at: {int(env.now)} minutes.\n")
                    yield env.timeout(TREATMENT_TIMES[patient.triage_level])
                treatment_end_time = env.now
                patient.treatment_time = treatment_end_time - treatment_start_time
                patient.total_time = patient.wait_time + patient.triage_time + patient.treatment_time
        else:
            with urgent_room.request() as req:
                treatment_start_time = env.now
                yield req
                with doctor_resource.request(priority=1) as doctor_req:
                    yield doctor_req
                    output_text.insert(END, f"Patient {patient.id} not having emergency neither urgency arrived at hospital at: {int(env.now)} minutes.\n")
                    yield env.timeout(TREATMENT_TIMES[patient.triage_level])
                treatment_end_time = env.now
                patient.treatment_time = treatment_end_time - treatment_start_time
                patient.total_time = patient.wait_time + patient.triage_time + patient.treatment_time


root = tk.Tk()
root.title('Hospital Emergency Room Simulation')
root.geometry("1366x768")
root['background']='#5fe0ec'

env = simpy.Environment()
waiting_room = simpy.Resource(env, capacity=10)
urgent_room = simpy.Resource(env, capacity=3)
emergency_room = simpy.Resource(env, capacity=1)
def run_simulation():
    doctor_resource = simpy.PriorityResource(env, capacity=NUM_DOCTORS)
    doctors = []
    for i in range(NUM_DOCTORS):
        doctors.append(f"Doctor {i+1}")
    env.process(patient_generator(env, ARRIVAL_RATE,TRIAGE_LEVELS, TREATMENT_TIMES, doctors, doctor_resource))
    env.run(until=SIM_TIME)

def click():
    newWindow = Toplevel(root)
    newWindow.title("Patient's Information")
    newWindow.geometry("1366x768")
    newWindow['background']='#5fe0ec'
    image1 = Image.open("Patients Info.png")
    image1 = image1.resize((600, 350))
    img = ImageTk.PhotoImage(image1)
    label4 = Label(newWindow, image=img)
    label4.place(x=50, y=50)
    output_text1=Text(newWindow,height=300)
    scroll_bar = tk.Scrollbar(newWindow)
    scroll_bar.pack(side=tk.LEFT)
    output_text1.pack(side=tk.RIGHT)
    output_text1.insert(END ,f"Average patient waiting time: {int(statistics.mean([patient.wait_time for patient in PATIENTS]))}.\n")
    output_text1.insert(END ,f"Average patient treatment time: {int(statistics.mean([patient.treatment_time for patient in PATIENTS]))}.\n")
    output_text1.insert(END ,f"\nInformation of the patients is as follows: \n")
    for i in PATIENTS:
        output_text1.insert(END ,f"Patient id: {i.id}.\n")
        output_text1.insert(END ,f"Arrival Time: {int(i.arrival_time)} minutes.\n")
        output_text1.insert(END ,f"Triage Level: {i.triage_level}.\n")
        output_text1.insert(END ,f"Treatment Time: {int(i.treatment_time)} minutes.\n")
        output_text1.insert(END ,f"Age: {i.age}.\n")
        output_text1.insert(END ,f"Sex: {i.sex}.\n")
        output_text1.insert(END, "\n")

    label5 = Label(newWindow, text = "Click below to exit!")
    label5.place(x=280,y=500)
    b4 = Button(newWindow, text="Exit", command=newWindow.destroy)
    b4.place(x=320,y=530)
    newWindow.mainloop()

image = Image.open("Hospital Reception.png")
image = image.resize((600, 350))
img = ImageTk.PhotoImage(image)
label = Label(root, image=img)
label.place(x=50,y=50)
output_text=Text(root,width=600,height=300)
output_text.place(x=700,y=50)
label1 = Label(root, text = "Click below to run the simulation")
label1.place(x=270, y=445)
b1 = Button(root, text = 'Run Simulation', command = run_simulation)
b1.place(x=320, y=470)
label2 = Label(root, text = "Click below to view Patient's Information")
label2.place(x=250,y=525)
b2 = Button(root, text = "Patient's Info", command = click)
b2.place(x=325, y=550)
def bar_graph(treatment_times):
  plt.bar(range(len(treatment_times)), treatment_times)
  plt.xlabel("Patient ID")
  plt.ylabel("Treatment Time (minutes)")
  plt.title("Treatment Time")
  plt.show()

def click():
  bar_graph([patient.treatment_time for patient in PATIENTS])
  
label3 = Label(root, text = "Click below for graph of treatment time!")
label3.place(x=250,y=600)
b4 = Button(root, text = "Bar Graph", command = click)
b4.place(x=325, y=625)
label6 = Label(root, text = "Click below to exit!")
label6.place(x=305,y=670)
b3 = Button(root, text = 'Exit', command=root.destroy)
b3.place(x=345,y=700)

root.mainloop()
