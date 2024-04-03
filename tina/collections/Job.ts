import {Collection} from "tinacms";

const Job: Collection = {
    name: "job",
    label: "Jobs",
    path: "data/jobs",
    format: "yaml",
    fields: [
        {
            type: "string",
            name: "title",
            label: "Title",
            required: true,
        },
        {
            type: "string",
            name: "company",
            label: "Company",
            required: true,
        },
        {
            type: "string",
            name: "website",
            label: "Website",
        },
        {
            type: "object",
            name: "range",
            label: "Range",
            fields: [
                {
                    type: "datetime",
                    name: "start",
                    label: "Start",
                    required: true,
                    ui: {
                        dateFormat: 'YYYY-MM',
                        parse: (value) => value && value.format('YYYY-MM'),
                    },
                },
                {
                    type: "datetime",
                    name: "end",
                    label: "End",
                    required: false,
                    ui: {
                        dateFormat: 'YYYY-MM',
                        parse: (value) => value && value.format('YYYY-MM'),
                    },
                },
                {
                    type: "boolean",
                    name: "current",
                    label: "Currently working there",
                    required: false,
                },
            ],
        },
        {
            type: "rich-text",
            name: "description",
            label: "Description",
            required: true,
        },
        {
            type: "string",
            name: "technologies",
            label: "Technologies",
            list: true,
        }
    ],
    ui: {
        filename: {
            readonly: true,
            slugify: (values) => {
                const date = new Date()
                return `${date.toISOString().split('T')[0]}_${values?.company?.toLowerCase().replace(/ /g, '-').replace(/\W/g, '')}`
            },
        },
    },
};

export default Job;
