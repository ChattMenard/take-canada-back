import { useEffect, useState } from "react";

export function useRemoteData(path, fallback) {
  const [data, setData] = useState(fallback);
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    const controller = new AbortController();

    fetch(path, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error(`Request failed (${response.status})`);
        return response.json();
      })
      .then((payload) => {
        setData(payload);
        setStatus("ready");
      })
      .catch((error) => {
        if (error.name !== "AbortError") setStatus("fallback");
      });

    return () => controller.abort();
  }, [path]);

  return { data, status };
}
