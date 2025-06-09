import zstandard as zstd

with open("war_logic.jsonl", "rb") as f_in:
    data = f_in.read()

cctx = zstd.ZstdCompressor()
with open("war_logic.jsonl.zst", "wb") as f_out:
    f_out.write(cctx.compress(data))

print("Compression complete. Check for war_logic.jsonl.zst")