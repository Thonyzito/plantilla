import fs from "fs";
import https from "https";

export async function descargarDesdePexels(query, index) {
  const apiKey = process.env.PEXELS_API_KEY;
  const url = `https://api.pexels.com/v1/search?query=${encodeURIComponent(query)}&per_page=1`;

  const options = {
    headers: { Authorization: apiKey },
  };

  return new Promise((resolve, reject) => {
    https.get(url, options, res => {
      let data = "";
      res.on("data", chunk => data += chunk);
      res.on("end", () => {
        const json = JSON.parse(data);
        const photo = json.videos?.[0] || json.photos?.[0];
        if (!photo) return resolve();

        const mediaUrl = photo.video_files?.[0]?.link || photo.src.medium;
        const filePath = `imagen_${index}.jpg`;

        https.get(mediaUrl, response => {
          const file = fs.createWriteStream(filePath);
          response.pipe(file);
          file.on("finish", () => file.close(resolve));
        });
      });
    }).on("error", reject);
  });
}
