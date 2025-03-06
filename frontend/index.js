import 'topobank/scss/custom.scss';

import DatasetDetail from './manager/DatasetDetail.vue';
import DatasetList from './manager/DatasetDetail.vue';

export const componentIndex = [
    {name: "dataset-list", implementation: DatasetList},
    {name: "dataset-detail", implementation: DatasetDetail}
];