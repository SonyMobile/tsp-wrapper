module.exports = {
    "extends": "google",
    "rules": {
        "indent": ["error", 4],
        "space-before-function-paren": ["error", {
            "anonymous": "always",
            "named": "never",
            //"asyncArrow": "always"
        }],
    }
};