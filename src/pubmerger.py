import yaml
import os


def merge_publications_into_cv():
    template_path = os.path.join("src", "Fabio_Calefato_CV_template.yaml")
    pubs_path = os.path.join("src", "bibliography", "selected_publications.yaml")
    output_path = os.path.join("src", "Fabio_Calefato_CV.yaml")

    with open(template_path, "r") as f:
        cv_data = yaml.safe_load(f)
    with open(pubs_path, "r") as f:
        pubs_data = yaml.safe_load(f)

    cv_data["cv"]["sections"]["selected_publications"] = pubs_data[
        "selected_publications"
    ]

    with open(output_path, "w") as f:
        yaml.dump(
            cv_data, f, sort_keys=False, allow_unicode=True, default_flow_style=False
        )


if __name__ == "__main__":
    merge_publications_into_cv()
