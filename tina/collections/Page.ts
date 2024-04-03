import {Collection} from "tinacms";

const Page: Collection = {
    name: "page",
    label: "Pages",
    path: "content",
    match: {
        include: "*",
    },
    format: "md",
    fields: [
        {
            type: "string",
            name: "title",
            label: "Title",
            isTitle: true,
            required: true,
        },
        {
            type: "rich-text",
            name: "body",
            label: "Body",
            isBody: true,
        },
    ],
    ui: {
        allowedActions: {
            delete: false,
        },
    },
};

export default Page;
