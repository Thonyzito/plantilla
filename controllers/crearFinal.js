import { exec } from "child_process";

export function crearFinal(modo) {
  return new Promise((res,rej)=>{
    exec(`python3 crear_final.py ${modo}`,(e,out,err)=>{
      e?rej(err):res(out);
    });
  });
}
