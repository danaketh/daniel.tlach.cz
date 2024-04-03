import {Collection} from "tinacms";

const BlogPost: Collection = {
    name: "blog",
    label: "Blog Posts",
    path: "content/blog",
    match: {
        include: "*",
        exclude: "_index",
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
            type: "datetime",
            label: "Date",
            name: "date",
        },
        {
            type: "boolean",
            name: "draft",
            label: "Draft",
        },
        {
            type: "rich-text",
            name: "body",
            label: "Body",
            isBody: true,
        },
        {
            type: "string",
            name: "tags",
            label: "Tags",
            list: true,
        }
    ],
    defaultItem: () => {
        return {
            date: new Date().toISOString(),
        }
    },
    ui: {
        filename: {
            readonly: true,
            slugify: (values) => {
                const date = new Date(values?.date)
                return `${date.toISOString().split('T')[0]}_${values?.title?.toLowerCase().replace(/ /g, '-')}`
            },
        },
    },
};

export default BlogPost;
