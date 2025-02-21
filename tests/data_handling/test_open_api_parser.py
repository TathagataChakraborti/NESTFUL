from nestful.data_handlers import get_catalog_from_openapi_specs
from nestful import Catalog, API
from pathlib import Path


class TestOpenAPISpecs:
    @staticmethod
    def get_abs_path(rel_path: str) -> Path:
        path_to_file = Path(__file__).parent.resolve()
        return Path.joinpath(path_to_file, rel_path).resolve()

    def test_read_nestful_catalog(self) -> None:
        rel_path_to_specs = "../../data_v1/executable/open_api_specs"
        abs_path = self.get_abs_path(rel_path_to_specs)

        catalog = get_catalog_from_openapi_specs(abs_path_to_specs=abs_path)
        assert len(catalog.apis) == 37

    def get_kubernetes_api(self, rel_path_to_specs: str) -> Catalog:
        abs_path = self.get_abs_path(rel_path_to_specs)

        catalog = get_catalog_from_openapi_specs(abs_path_to_specs=abs_path)
        return catalog

    def test_read_kubernetes_api_by_directory(self) -> None:
        rel_path_to_specs = "./open_api_specs"
        kube_catalog = self.get_kubernetes_api(rel_path_to_specs)

        assert len(kube_catalog.apis) == 322

    def test_read_kubernetes_api_by_file(self) -> None:
        rel_path_to_specs = "./open_api_specs/kubeappsapi.json"
        kube_catalog = self.get_kubernetes_api(rel_path_to_specs)

        assert len(kube_catalog.apis) == 77

    def test_rogue_parameters(self) -> None:
        rel_path_to_specs = "./open_api_specs/kubeappsapi.json"
        kube_catalog = self.get_kubernetes_api(rel_path_to_specs)

        test_api = kube_catalog.get_api(
            name="listAppsV1ControllerRevisionForAllNamespaces"
        )

        assert isinstance(test_api, API)
        assert len(test_api.query_parameters) == 11

        test_api = kube_catalog.get_api(
            name="deleteAppsV1CollectionNamespacedControllerRevision"
        )

        assert isinstance(test_api, API)
        assert len(test_api.query_parameters) == 19
