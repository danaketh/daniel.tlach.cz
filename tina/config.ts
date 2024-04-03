import {defineConfig} from "tinacms";
import BlogPost from "./collections/BlogPost";
import Page from "./collections/Page";

const branch = "main";

export default defineConfig({
    branch,
    clientId: process.env.TINA_PUBLIC_CLIENT_ID,
    token: process.env.TINA_TOKEN,

    build: {
        outputFolder: "admin",
        publicFolder: "static",
    },
    media: {
        tina: {
            mediaRoot: "",
            publicFolder: "static",
        },
    },
    schema: {
        collections: [
            BlogPost,
            Page,
        ],
    },
});
