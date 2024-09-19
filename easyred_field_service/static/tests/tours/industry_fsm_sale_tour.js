/** @odoo-module */
import "@industry_fsm/js/tours/industry_fsm_tour";
import {_t} from "@web/core/l10n/translation";
import {markup} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {registry} from "@web/core/registry";

patch(registry.category("web_tour.tours").get("industry_fsm_tour"), {
    steps() {
        const originalSteps = super.steps();
        const fsmStartStepIndex = originalSteps.findIndex((step) => step.id === "fsm_start");
        originalSteps.splice(fsmStartStepIndex + 1, 0, {
            trigger: "input#is_saleorder_1",
            content: markup(_t("Let's <b>activate saleorders</b> to show action_fsm_view_material button")),
        });
        return originalSteps;
    },
});
