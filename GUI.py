import tkinter as tk
from tkinter import ttk,messagebox
import numpy as np,pandas as pd,joblib,os

CM,RM="CatBoost_CFST.joblib","GPR_CFST.joblib"

CF=["D","t","L","fc","Ec","fy","fu","Es","D_t","L_D","Total Area","Ac","As","kesay","dov"]
RF=["B","H","t","L","fc","Ec","fy","fu","Es","H_B","B_t","H_t","L_B","L_H","Total Area","Ac","As","kesay","dov"]

CI=[
("D","Outer diameter (D)","mm"),("t","Steel tube thickness (t)","mm"),
("L","Column length (L)","mm"),("fc","Concrete compressive strength (f'c)","MPa"),
("Ec","Concrete elastic modulus (Ec)","GPa"),("fy","Steel yield strength (fy)","MPa"),
("fu","Steel ultimate strength (fu)","MPa"),("Es","Steel elastic modulus (Es)","GPa"),
("dov","Corrosion level (Dov)","%")]

RI=[
("B","Section width (B)","mm"),("H","Section depth (H)","mm"),
("t","Steel tube thickness (t)","mm"),("L","Column length (L)","mm"),
("fc","Concrete compressive strength (f'c)","MPa"),("Ec","Concrete elastic modulus (Ec)","GPa"),
("fy","Steel yield strength (fy)","MPa"),("fu","Steel ultimate strength (fu)","MPa"),
("Es","Steel elastic modulus (Es)","GPa"),("dov","Corrosion level (Dov)","%")]

cm=rm=None

def load():
    global cm,rm
    try:
        for p,n in [(CM,"Circular"),(RM,"Rectangular")]:
            if not os.path.exists(p):raise FileNotFoundError(f"{n} model was not found:\n\n{p}")
        cm,rm=joblib.load(CM),joblib.load(RM);return 1
    except Exception as e:messagebox.showerror("Model Loading Error",e);return 0


class GUI:
    def __init__(self,r):
        self.r=r;r.title("CFST Ultimate Load Prediction Tool");r.geometry("800x800");r.resizable(0,0)
        self.e={};self.sec=tk.StringVar(value="Circular");self.model=tk.StringVar(value="CatBoost");self.out=tk.StringVar(value="---")
        self.style();self.header();self.selector();self.inputs();self.result();self.buttons();self.update()

    def style(self):
        s=ttk.Style()
        try:s.theme_use("clam")
        except:pass
        for n,f in {"Title.TLabel":("Segoe UI",21,"bold"),"Subtitle.TLabel":("Segoe UI",10),
        "Section.TLabelframe.Label":("Segoe UI",11,"bold"),"Parameter.TLabel":("Segoe UI",10),
        "Unit.TLabel":("Segoe UI",9),"Result.TLabel":("Segoe UI",20,"bold"),
        "Predict.TButton":("Segoe UI",11)}.items():s.configure(n,font=f)

    def header(self):
        ttk.Label((f:=ttk.Frame(self.r)),text="CFST Ultimate Load Prediction Tool",
                  style="Title.TLabel").pack();f.pack(fill="x",padx=30,pady=(20,10))

    def selector(self):
        f=ttk.LabelFrame(self.r,text="Section Type",padding=12);f.pack(fill="x",padx=30,pady=8)
        for t,v in [("Circular","Circular"),("Rectangular","Rectangular")]:
            ttk.Radiobutton(f,text=t,variable=self.sec,value=v,command=self.update).pack(side="left",padx=25)
        ttk.Label(f,text="Prediction model:").pack(side="left",padx=(100,8))
        ttk.Label(f,textvariable=self.model,font=("Segoe UI",10)).pack(side="left")

    def inputs(self):
        self.box=ttk.LabelFrame(self.r,text="Primary Input Parameters",padding=15)
        self.box.pack(fill="x",padx=30,pady=8)

    def build(self):
        [w.destroy() for w in self.box.winfo_children()];self.e={}
        for i,(k,d,u) in enumerate(CI if self.sec.get()=="Circular" else RI):
            r,c=i%5,i//5*3
            ttk.Label(self.box,text=d,style="Parameter.TLabel").grid(row=r,column=c,padx=(8,5),pady=8,sticky="w")
            self.e[k]=ttk.Entry(self.box,width=14);self.e[k].grid(row=r,column=c+1,padx=5,pady=8)
            ttk.Label(self.box,text=u,style="Unit.TLabel").grid(row=r,column=c+2,padx=(0,25),pady=8,sticky="w")

    def result(self):
        f=ttk.LabelFrame(self.r,text="Prediction Result",padding=15);f.pack(fill="x",padx=30,pady=10)
        ttk.Label(f,text="Predicted Ultimate Load, Nu:",font=("Segoe UI",12)).pack(side="left",padx=10)
        ttk.Label(f,textvariable=self.out,style="Result.TLabel").pack(side="left",padx=10)
        ttk.Label(f,text="kN",font=("Segoe UI",12)).pack(side="left")

    def buttons(self):
        f=ttk.Frame(self.r);f.pack(pady=12)
        for i,(t,c) in enumerate([("Predict",self.predict),("Clear",self.clear)]):
            ttk.Button(f,text=t,style="Predict.TButton",command=c,width=15).grid(row=0,column=i,padx=10)

    def update(self):
        self.model.set("CatBoost" if self.sec.get()=="Circular" else "GPR");self.build();self.out.set("---")

    def validate(self):
        p=CI if self.sec.get()=="Circular" else RI;v={}
        for k,d,_ in p:
            z=self.e[k].get().strip()
            if not z:return self.err("Missing Input",f"Please enter a value for:\n\n{d}",k)
            try:x=float(z)
            except:return self.err("Invalid Input",f"The value entered for:\n\n{d}\n\nmust be numeric.",k)
            if not np.isfinite(x):return self.err("Invalid Input",f"{d} must be a finite number.",k)
            if k!="dov" and x<=0:return self.err("Invalid Value",f"{d} must be greater than zero.",k)
            if k=="dov" and not 0<=x<=100:return self.err("Invalid Corrosion Level","Corrosion level must be between 0 and 100%.",k)
            v[k]=x
        if self.sec.get()=="Circular" and v["D"]<=2*v["t"]:
            messagebox.showerror("Invalid Geometry","For a circular section:\n\nD must be greater than 2t.");return
        if self.sec.get()=="Rectangular" and (v["B"]<=2*v["t"] or v["H"]<=2*v["t"]):
            messagebox.showerror("Invalid Geometry","For a rectangular section:\n\nB and H must be greater than 2t.");return
        return v

    def err(self,title,msg,k):
        messagebox.showerror(title,msg);self.e[k].focus()

    def features(self,x):
        if self.sec.get()=="Circular":
            D,t,L,fc,fy,d=x["D"],x["t"],x["L"],x["fc"],x["fy"],x["dov"]
            A=np.pi*D**2/4;ac=np.pi*(D-2*t)**2/4;As=(A-ac)*(1-d/100)
            return [D/t,L/D,A,ac,As,As*fy/(ac*fc)]
        B,H,t,L,fc,fy=x["B"],x["H"],x["t"],x["L"],x["fc"],x["fy"]
        A=B*H;ac=(B-2*t)*(H-2*t);As=A-ac
        return [H/B,B/t,H/t,L/B,L/H,A,ac,As,As*fy/(ac*fc)]

    def dataframe(self,x,d):
        keys=["D","t","L","fc","Ec","fy","fu","Es"] if self.sec.get()=="Circular" else ["B","H","t","L","fc","Ec","fy","fu","Es"]
        return pd.DataFrame([[*[x[k] for k in keys],*d,x["dov"]]],
                            columns=CF if self.sec.get()=="Circular" else RF)

    def predict(self):
        x=self.validate()
        if x is None:return
        try:
            c=self.sec.get()=="Circular";m=cm if c else rm
            if m is None:raise RuntimeError(f"{'Circular CatBoost' if c else 'Rectangular GPR'} model is not loaded.")
            y=m.predict(self.dataframe(x,self.features(x)))[0]
            if not np.isfinite(y):raise ValueError("The model returned an invalid prediction.")
            self.out.set(f"{y:,.2f}")
        except Exception as e:messagebox.showerror("Prediction Error",e)

    def clear(self):
        [e.delete(0,tk.END) for e in self.e.values()];self.out.set("---")


if __name__=="__main__":
    r=tk.Tk()
    if not load():r.destroy()
    else:GUI(r);r.mainloop()
