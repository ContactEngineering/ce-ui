export function countTaskStates(analyses, states) {
    if (analyses == null) {
        return 0;
    }
    let count = 0;
    for (const analysis of analyses) {
        if (states.includes(analysis.task_state)) {
            count += 1;
        }
    }
    return count;
}
