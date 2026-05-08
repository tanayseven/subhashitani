import json

from flask import Flask, Response, render_template
from flask_frozen import Freezer

from shlokas import load_all_shlokas

app = Flask(__name__)
app.config["FREEZER_DESTINATION"] = "build"
app.config["FREEZER_RELATIVE_URLS"] = True

freezer = Freezer(app)


@app.route("/")
def index():
    shlokas = load_all_shlokas()
    return render_template("index.html", recent=shlokas[:10], total=len(shlokas))


@app.route("/shlokas/<slug>.html")
def shloka_page(slug: str):
    shloka = next((s for s in load_all_shlokas() if s.slug == slug), None)
    return render_template("shloka.html", shloka=shloka)


@app.route("/search.json")
def search_json():
    data = [
        {
            "slug": s.slug,
            "title": s.title,
            "source": s.source,
            "tags": s.tags,
            "date": s.date.isoformat(),
            "shloka": s.shloka_text,
            "translation_languages": s.translation_languages,
            "url": f"/shlokas/{s.slug}.html",
        }
        for s in load_all_shlokas()
    ]
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        mimetype="application/json",
    )


# Frozen-Flask needs explicit URL values for parameterised routes.
# Naming this the same as the view is the frozen-flask convention;
# Flask's internal routing table keeps its own reference to the view.
@freezer.register_generator
def shloka_page():
    for shloka in load_all_shlokas():
        yield {"slug": shloka.slug}


def freeze():
    freezer.freeze()


def serve():
    app.run(debug=True)


if __name__ == "__main__":
    serve()