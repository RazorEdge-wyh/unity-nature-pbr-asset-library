"""Download Poly Haven HDRIs (1k .hdr) for skybox / IBL use."""
import os
import sys
import concurrent.futures as cf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib

HDRIS = ["kloofendal_48d_partly_cloudy_puresky", "kloppenheim_02", "kloppenheim_06_puresky",
         "spruit_sunrise", "kiara_1_dawn", "the_sky_is_on_fire", "venice_sunset",
         "lilienstein", "meadow_2", "moonless_golf", "dikhololo_night", "satara_night"]


def build(name):
    man = lib.load_json(os.path.join(lib.MAN, "hdris", name + ".json"))
    f = man["hdri"]["1k"]["hdr"]
    outdir = os.path.join(lib.ENV, "HDRIs")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name + ".hdr")
    lib.download(f["url"], path)
    return {"name": name, "category": "HDRI", "type": "hdri",
            "source": "Poly Haven", "sourceUrl": "https://polyhaven.com/a/%s" % name,
            "license": "CC0", "resolution": 1024,
            "path": "Environment/HDRIs/%s.hdr" % name}


def main():
    entries = []
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(build, n): n for n in HDRIS}
        for f in cf.as_completed(futs):
            try:
                entries.append(f.result())
                print("hdri ok", futs[f])
            except Exception as e:  # noqa: BLE001
                print("hdri FAIL", futs[f], repr(e)[:200])
    lib.dump_json(os.path.join(lib.DOCS, "hdris.json"), entries)
    print("hdris done:", len(entries))


if __name__ == "__main__":
    main()
