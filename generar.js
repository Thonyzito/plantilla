import { exec } from "child_process";

export function generarContenido({ modo }) {
  return new Promise((resolve, reject) => {
    exec(`python3 crear_final.py ${modo}`, (err, stdout, stderr) => {
      if (err) return reject(stderr);
      resolve(stdout);
    });
  });
}
