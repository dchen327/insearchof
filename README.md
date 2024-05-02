This is a [Next.js](https://nextjs.org/) project bootstrapped with [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).

## Project Contributors

The project development was split between our project's features. Each person designed their own features, wrote code for it, documented it, tested it, and deployed it. They are:

The marketplace page, where uploaded items and requests are displayed to the buyer or request fulfiller. This was developed by David.

The sell and rent page, where items can be uploaded onto the marketplace. The website will ask for details (such as title, price, etc.) so it can be properly presented in the marketplace. This was developed by Henry.

The ISO requester page is similar to the sell and rent page. Here, those who need an item can upload their request. They can also update (edit) their already existing request, mark their request as complete (i.e. their request has been fulfilled), and they can delete the request. This was developed by Brian.

The profiles page contains the user's profile information, such as their contact information, previous transactions, and their items/requests currently on the marketplace. This was developed by Arushi.

David also set up the development environment. 

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.js`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/basic-features/font-optimization) to automatically optimize and load Inter, a custom Google Font.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js/) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/deployment) for more details.

## Running Tests

To emulate our database for tests, we use the Firebase-emulator. Install firebase using `npm install firebase`. 
You must then initialize the current working directory as a Firebase project using `firebase init`. 
You will be given several Firebase features. Please select `Firestore` and `storage`. You only need to do this once!
Then type `firebase emulators:start`. You can check the Firestore emulator here: `http://127.0.0.1:4001/firestore`
and the Storage emulator here: `http://127.0.0.1:4001/storage`. To run the tests, change your current directory to
InSearchOf and type `python .\api\{test_file}.py`, where `test_file` can be `catalog_test`, `insearchof_test`, `sellList_test`, or `profiles_test`. 
