import '@/scss/custom.scss';

import AnalysisResultsDetail from "@/pages/AnalysisResultsDetail.vue";
import AnalysisResultsList from "@/pages/AnalysisResultsList.vue";
import DatasetCollection from '@/pages/DatasetCollection.vue';
import DatasetCollectionList from '@/pages/DatasetCollectionList.vue';
import DatasetCollectionPublish from '@/pages/DatasetCollectionPublish.vue';
import DatasetDetail from '@/pages/DatasetDetail.vue';
import DatasetList from '@/pages/DatasetList.vue';
import DatasetPublish from '@/pages/DatasetPublish.vue';
import Home from '@/pages/Home.vue';
import TopographyDetail from '@/pages/TopographyDetail.vue';

/*
 * Page components are mounted by the Django view through the AppFrame
 * component; the registered names below must match the `vue_component`
 * values passed by the `ce_ui` Django app.
 */
const pageComponents: { [name: string]: any } = {
    AnalysisDetail: AnalysisResultsDetail,
    AnalysisList: AnalysisResultsList,
    DatasetCollection: DatasetCollection,
    DatasetCollectionList: DatasetCollectionList,
    DatasetCollectionPublish: DatasetCollectionPublish,
    DatasetDetail: DatasetDetail,
    DatasetList: DatasetList,
    DatasetPublish: DatasetPublish,
    Home: Home,
    TopographyDetail: TopographyDetail,
};

export function registerPageComponents(app) {
    for (const [name, implementation] of Object.entries(pageComponents)) {
        app.component(name, implementation);
    }
}
