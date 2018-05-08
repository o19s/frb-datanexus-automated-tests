pm.test("Number of matches", function () {
    console.log('matches = ' + pm.response.json().grouped.$grouping_value.matches);
    console.log('ngroups = ' + pm.response.json().grouped.$grouping_value.ngroups);
    pm.expect(pm.response.json().grouped.$grouping_value.matches).to.equal(expected_matches);
    pm.expect(pm.response.json().grouped.$grouping_value.ngroups).to.equal(expected_matches_grouped);
});