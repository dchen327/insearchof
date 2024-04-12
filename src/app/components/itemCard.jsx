import Image from "next/image";

export const ItemCard = ({ item }) => {
  return (
    <div className="card is-shadowless">
      <div className="card-content px-4 py-2">
        <div className="media mb-2">
          <div className="media-content">
            <p className="title is-4">{item.title}</p>
            <p className="subtitle is-6">{item.sellerUserID}</p>
          </div>
        </div>
        <div className="content">
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus nec
          iaculis mauris.
        </div>
      </div>
      {/* <div className="card-image ">
        <figure className="image is-4by3">
          <Image src={item.images[0]} alt="Image" fill={true} />
        </figure>
      </div> */}
    </div>
  );
};
