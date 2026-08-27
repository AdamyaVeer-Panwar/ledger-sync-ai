from app.domain.synthetic.validator import validate_dataset
from app.domain.synthetic.generator import DatasetGenerator

def test_generated_dataset_is_valid():
    dataset = DatasetGenerator(
        records=400,
        seed=42,
    ).generate()

    validate_dataset(dataset)