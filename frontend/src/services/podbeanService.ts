export async function publishToPodbeanMCP(
    audioUrl: string,
    notes: string
  ): Promise<any> {
    const resp = await fetch("/api/podbean/publish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ audioUrl, notes }),
    });
    if (!resp.ok) throw new Error(await resp.text());
    return resp.json();
  }